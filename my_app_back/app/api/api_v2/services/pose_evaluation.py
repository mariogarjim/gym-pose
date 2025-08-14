import typing as t

import numpy as np
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.api.api_v2.schemas.exercise import (
    FinalEvaluation,
)
from app.api.api_v2.schemas.feedback import Feedback
from app.api.api_v2.schemas.video import (
    ExerciseEnum,
    VideoMetadata,
    Viewpoint,
)
from app.api.api_v2.services.video import VideoService, VideoServiceFactory
from app.enum import ExerciseMeasureEnum

HARDCODED_VIEWPOINTS = [
    Viewpoint.FRONT,
]


class PoseEvaluationService:
    def __init__(self):
        self.video_services: t.List[VideoService] = []

    async def evaluate_pose(
        self,
        files: t.List[UploadFile],
        exercise_type: ExerciseEnum,
        video_files_metadata: t.Optional[t.List[VideoMetadata]],
    ) -> StreamingResponse:
        """
        Process videos and return a streaming response.
        """
        for file in files:
            if not file.content_type.startswith("video/"):
                raise HTTPException(status_code=400, detail="File must be a video")

        output_feedback: t.List[Feedback] = []
        final_evaluations_videos: t.List[
            dict[ExerciseMeasureEnum, list[np.ndarray]]
        ] = []

        for file, viewpoint in zip(files, HARDCODED_VIEWPOINTS):
            video_path = await VideoServiceFactory.save_to_temp_file(file)

            video_service = VideoServiceFactory.get_video_service(video_path, viewpoint)
            self.video_services.append(video_service)

            video_service.process_video(exercise_type)

            final_evaluation: FinalEvaluation = video_service.get_final_evaluation()

            output_feedback.append(final_evaluation.feedback)
            final_evaluations_videos.append(final_evaluation.videos)

        output_feedback = video_service.feedback_service.summarize_final_evaluation(
            output_feedback, exercise_type
        )

        print(f"final_evaluations_videos: {final_evaluations_videos}")

        output_video_paths = []
        for index in range(len(self.video_services)):
            for exercise_measure, frames in final_evaluations_videos[index].items():
                output_video_paths.append(
                    self.video_services[index].encode_frames_to_video(
                        frames=frames,
                        extra_name=f"{exercise_measure.value}_{self.video_services[index].viewpoint.value}",
                    )
                )

        print(f"output_feedback: {output_feedback}")

        zip_buffer = VideoServiceFactory.process_videos_response(output_video_paths)

        print("Returning streaming response")
        return StreamingResponse(
            zip_buffer,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=analysis_results.zip",
                "X-Exercise-Feedback": output_feedback.model_dump_json(),
            },
        )
