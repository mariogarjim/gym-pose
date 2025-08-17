import os
import typing as t
import uuid

import boto3
import numpy as np
from fastapi import HTTPException, UploadFile

from app.api.api_v2.schemas.exercise import (
    FinalEvaluation,
)
from app.api.api_v2.schemas.feedback import Feedback
from app.api.api_v2.schemas.pose import OutputPose
from app.enum import ExerciseEnum, Viewpoint
from app.api.api_v2.services.video import VideoService, VideoServiceFactory
from app.enum import ExerciseMeasureEnum

HARDCODED_VIEWPOINTS = [
    Viewpoint.FRONT,
]


class PoseEvaluationService:
    def __init__(self):
        self.video_services: t.List[VideoService] = []
        self.s3_client = boto3.client("s3")

    def evaluate_pose(
        self,
        files: t.Union[t.List[UploadFile], t.List[str]],
        user_id: str,
        exercise_type: ExerciseEnum,
    ) -> OutputPose:
        """
        Process videos and return a streaming response.

        files: The list of files to process. Can be a list of UploadFile or a list of temp file paths.
        exercise_type: The exercise type to process.
        """
        output_feedback: t.List[Feedback] = []
        final_evaluations_videos: t.List[
            dict[ExerciseMeasureEnum, list[np.ndarray]]
        ] = []

        if isinstance(files, list) and all(
            isinstance(file, UploadFile) for file in files
        ):
            for file in files:
                if not file.content_type.startswith("video/"):
                    raise HTTPException(status_code=400, detail="File must be a video")

        for file, viewpoint in zip(files, HARDCODED_VIEWPOINTS):
            if isinstance(file, UploadFile):
                video_path = VideoServiceFactory.save_to_temp_file(file)
            else:
                video_path = file

            video_service = VideoServiceFactory.get_video_service(video_path, viewpoint)
            self.video_services.append(video_service)

            video_service.process_video(exercise_type)

            final_evaluation: FinalEvaluation = video_service.get_final_evaluation()

            print("########################")
            print("Final evaluation: ", final_evaluation.feedback)
            print("########################")

            output_feedback.append(final_evaluation.feedback)
            final_evaluations_videos.append(final_evaluation.videos)

        output_feedback = video_service.feedback_service.summarize_final_evaluation(
            output_feedback, exercise_type
        )

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
        processed_key = f"processed/{user_id}/{exercise_type.value}/{uuid.uuid4()}.zip"

        self.s3_client.put_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=processed_key,
            Body=zip_buffer,
        )

        print("Returning streaming response")
        return OutputPose(
            key=processed_key,
            url=f"https://{os.getenv('S3_BUCKET_NAME')}.s3.amazonaws.com/{processed_key}",
        )
