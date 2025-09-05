import io
import os
import tempfile
import typing as t
from zipfile import ZipFile

import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException, UploadFile

from app.api.api_v2.schemas.video import VideoMetadata
from app.api.api_v2.services.exercise import ExerciseFactory
from app.api.api_v2.services.feedback import FeedbackService
from app.enum import ExerciseEnum, Viewpoint
from app.api.api_v2.schemas.exercise import ExerciseFinalEvaluation


class VideoService:
    def __init__(self, feedback_service: FeedbackService):
        self.mp_pose = mp.solutions.pose
        self.feedback_service = feedback_service

        self.video_metadata: t.List[VideoMetadata] = []
        self.video_paths: t.List[str] = []

    def set_video_params(self, video_path: str, viewpoint: Viewpoint) -> None:
        """Preprocess the video."""
        self.viewpoint = viewpoint
        cap = cv2.VideoCapture(video_path)

        # Get the video metadata
        self.fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) else 30
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Get the video dimensions
        ok, frame = cap.read()
        if not ok:
            cap.release()
            raise RuntimeError(
                f"Could not read the first frame of the video in {video_path}"
            )
        self.video_path = video_path
        h, w = frame.shape[:2]

        # check if the video is vertical
        print(f"h: {h}, w: {w}")
        is_vertical = h > w
        if not is_vertical:
            raise HTTPException(
                status_code=400,
                detail=f"The video is not vertical. h: {h}, w: {w}. Please upload a vertical video.",
            )

    def _get_exercise_service(self, exercise_type: ExerciseEnum, total_frames: int):
        """Set the exercise service based on the exercise type.
        One exercise service is created for each differente viewpoint.
        """
        return ExerciseFactory.get_exercise_strategy_service(
            exercise_type, total_frames
        )

    def _set_exercise_service(self, exercise_type: ExerciseEnum, total_frames: int):
        self.exercise_service = self._get_exercise_service(exercise_type, total_frames)

    def process_video(
        self,
        exercise_type: ExerciseEnum,
    ) -> None:
        """Process a video file and analyze exercise form."""
        cap = cv2.VideoCapture(self.video_path)
        frame_count = 0

        self.exercise_service = self._get_exercise_service(
            exercise_type, self.total_frames
        )

        with self.mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb_frame)
                landmarks = result.pose_landmarks

                if landmarks:
                    self.exercise_service.evaluate_frame(
                        frame_img=frame,
                        frame_index=frame_count,
                        landmarks=landmarks,
                    )

                print(f"Processing frame {frame_count}...")

                frame_count += 1

            cap.release()

        print(f"video path: {self.video_path} processed")

    def get_final_evaluation(self) -> ExerciseFinalEvaluation:
        self._clean_temp_file()
        return self.exercise_service.get_final_evaluation()

    def _clean_temp_file(self) -> None:
        """Clean up the temporary files."""
        if os.path.exists(self.video_path):
            os.remove(self.video_path)

    def encode_frames_to_video(
        self, frames: list[np.ndarray], extra_name: str
    ) -> bytes:
        if not frames:
            return None
        height, width, _ = frames[0].shape
        temp_fd, temp_path = tempfile.mkstemp(suffix=f"_{extra_name}.mp4")
        os.close(temp_fd)

        out = cv2.VideoWriter(
            temp_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            (width, height),
        )

        for frame in frames:
            out.write(frame)
        out.release()

        return temp_path


class VideoServiceFactory:
    @staticmethod
    def get_video_service(video_path: str, viewpoint: Viewpoint) -> VideoService:
        """Get the video service for the given video path."""
        feedback_service = FeedbackService()

        video_service = VideoService(feedback_service)
        video_service.set_video_params(video_path, viewpoint)
        return video_service

    @staticmethod
    async def save_to_temp_file(file: UploadFile) -> str:
        """Save the video file to a temporary file."""
        video_fd, video_path = tempfile.mkstemp(suffix=".mp4")
        os.close(video_fd)

        with open(video_path, "wb") as f:
            content = await file.read()
            f.write(content)

        return video_path

    @staticmethod
    def process_videos_response(
        video_paths: t.List[str],
    ) -> io.BytesIO:
        """Process the videos and return a zip file."""
        print("Processing videos response")
        root_dir_name = "videos"
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_archive:
            for video_path in video_paths:
                arcname = os.path.join(root_dir_name, os.path.basename(video_path))
                zip_archive.write(video_path, arcname=arcname)

        zip_buffer.seek(0)
        return zip_buffer
