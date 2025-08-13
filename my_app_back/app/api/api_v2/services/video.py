import io
import os
import tempfile
import typing as t
from io import BytesIO
from zipfile import ZipFile

import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.api.api_v2.schemas.video import VideoMetadata
from app.api.api_v2.services.exercise import ExerciseFactory, BaseExerciseService
from app.api.api_v2.services.feedback import FeedbackService
from app.enum import ExerciseEnum, ExerciseMeasureEnum, Viewpoint
from app.api.api_v2.schemas.exercise import FinalEvaluation


class VideoService:
    def __init__(self, feedback_service: FeedbackService):
        self.feedback_service = feedback_service
        self.mp_pose = mp.solutions.pose

        self.summarized_final_evaluation: FinalEvaluation = None
        self.video_metadata: t.List[VideoMetadata] = []
        self.video_paths: t.List[str] = []

        self.exercise_service_map: dict[Viewpoint, BaseExerciseService] = {}

    def _get_exercise_service(self, exercise_type: ExerciseEnum, total_frames: int):
        """Set the exercise service based on the exercise type.
        One exercise service is created for each differente viewpoint.
        """
        return ExerciseFactory.get_exercise_strategy_service(
            exercise_type, total_frames
        )

    def _set_exercise_service(self, exercise_type: ExerciseEnum, total_frames: int):
        self.exercise_service = self._get_exercise_service(exercise_type, total_frames)

    async def _save_to_temp_file(self, file: UploadFile) -> str:
        """Save the video file to a temporary file."""
        video_fd, video_path = tempfile.mkstemp(suffix=".mp4")
        os.close(video_fd)

        with open(video_path, "wb") as f:
            content = await file.read()
            f.write(content)

        self.video_paths.append(video_path)

        return video_path

    def _process_video(
        self,
        video_path: str,
        exercise_type: ExerciseEnum,
        metadata: t.Optional[VideoMetadata],
    ) -> None:
        """Process a video file and analyze exercise form."""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        if not metadata:
            metadata = VideoMetadata(
                fps=cap.get(cv2.CAP_PROP_FPS),
                total_frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                viewpoint=Viewpoint.FRONT,
            )
            self.video_metadata.append(metadata)

        self.exercise_service = self._get_exercise_service(
            exercise_type, metadata.total_frames
        )
        self.exercise_service_map[metadata.viewpoint] = self.exercise_service

        with self.mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb_frame)
                landmarks = result.pose_landmarks

                if landmarks:
                    self.exercise_service_map[metadata.viewpoint].evaluate_frame(
                        frame_img=frame,
                        frame=frame_count,
                        landmarks=landmarks,
                    )

                frame_count += 1

            cap.release()

    def _clean_temp_files(self) -> None:
        """Clean up the temporary files."""
        for path in self.video_paths:
            if os.path.exists(path):
                os.remove(path)

    def _encode_frames_to_video(
        self, frames: list[np.ndarray], extra_name: str, index: int, fps: int
    ) -> bytes:
        if not frames:
            return None
        height, width, _ = frames[0].shape
        temp_fd, temp_path = tempfile.mkstemp(suffix=f"_{extra_name}_{index}.mp4")
        os.close(temp_fd)

        out = cv2.VideoWriter(
            temp_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )

        for frame in frames:
            out.write(frame)
        out.release()

        return temp_path

    def _process_videos_response(
        self,
        videos: dict[ExerciseMeasureEnum, list[np.ndarray]],
        video_metadata: t.List[VideoMetadata],
    ) -> io.BytesIO:
        """Process the videos and return a zip file."""
        root_dir_name = "videos"
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_archive:
            index = 0
            for video in videos:
                fps = video_metadata[index].fps
                for feedback, frames in video.items():
                    video_path = self._encode_frames_to_video(
                        frames, feedback.value, index, fps
                    )
                    if video_path:
                        arcname = os.path.join(
                            root_dir_name, feedback.value, os.path.basename(video_path)
                        )
                    zip_archive.write(video_path, arcname=arcname)
                    index += 1

        zip_buffer.seek(0)
        return zip_buffer

    async def upload_and_process(
        self,
        files: t.List[UploadFile],
        exercise_type: ExerciseEnum,
        video_metadata: t.Optional[t.List[VideoMetadata]],
    ) -> StreamingResponse:
        """
        Process videos and return a streaming response.
        """

        for file in files:
            if not file.content_type.startswith("video/"):
                raise HTTPException(status_code=400, detail="File must be a video")

        for file in files:
            video_path = await self._save_to_temp_file(file)

        if video_metadata:
            for video_path, metadata in zip(self.video_paths, video_metadata):
                self._process_video(video_path, exercise_type, metadata)
        else:
            for video_path in self.video_paths:
                self._process_video(video_path, exercise_type, metadata=None)

        final_evaluations_feedback = []
        final_evaluations_videos = []
        for viewpoint_exercise_service in self.exercise_service_map.values():
            final_evaluation = viewpoint_exercise_service.get_final_evaluation()
            final_evaluations_feedback.append(final_evaluation.feedback)
            final_evaluations_videos.append(final_evaluation.videos)

        output_feedback = self.feedback_service.summarize_final_evaluation(
            final_evaluations_feedback, exercise_type
        )

        zip_buffer = self._process_videos_response(
            final_evaluations_videos, self.video_metadata
        )

        self._clean_temp_files()

        return StreamingResponse(
            zip_buffer,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=analysis_results.zip",
                "X-Exercise-Feedback": output_feedback.model_dump_json(),
            },
        )
