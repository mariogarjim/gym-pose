import io
import tempfile
import zipfile
import os
import typing as t

import boto3
import numpy as np

from app.api.api_v2.schemas.exercise import (
    ExerciseFeedback,
)
from app.api.api_v2.schemas.feedback import Feedback
from app.api.api_v2.schemas.pose import OutputPose
from app.enum import ExerciseEnum, Viewpoint
from app.api.api_v2.services.video import VideoService, VideoServiceFactory
from app.enum import ExerciseMeasureEnum

HARDCODED_VIEWPOINTS = [
    Viewpoint.SIDE,
]


class PoseEvaluationService:
    def __init__(self):
        self.video_services: t.List[VideoService] = []
        # Use the learning-env profile for AWS operations
        session = boto3.Session(profile_name="learning-env")
        self.s3_client = session.client("s3")

    def unzip_videos_to_temp(self, zip_bytes: bytes) -> list[str]:
        """
        Unzips a ZIP file from bytes into unique temporary directories.
        Returns a list of paths to the extracted video files.
        """
        extracted_files = []

        # Create a unique temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                z.extractall(tmpdir)

            # Walk through and collect all files
            for root, _, files in os.walk(tmpdir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    extracted_files.append(file_path)

            # Here tmpdir will be deleted when this function ends
            # If you want to keep files longer, copy them into /tmp
            # (Lambda has /tmp with 512MB–10GB space)
            final_paths = []
            for f in extracted_files:
                dest_path = os.path.join("/tmp", os.path.basename(f))
                os.rename(f, dest_path)  # or shutil.copy if you want to keep original
                final_paths.append(dest_path)

            return final_paths

    def evaluate_pose(
        self,
        file_content: bytes,
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

        video_paths = self.unzip_videos_to_temp(file_content)

        for video_path, viewpoint in zip(video_paths, HARDCODED_VIEWPOINTS):
            video_service = VideoServiceFactory.get_video_service(video_path, viewpoint)
            self.video_services.append(video_service)

            video_service.process_video(exercise_type)

            final_evaluation: dict[ExerciseMeasureEnum, ExerciseFeedback] = (
                video_service.get_final_evaluation()
            )

            print("########################")
            print("Final evaluation: ", final_evaluation)
            print("########################")

            output_feedback.append(final_evaluation)

        output_feedback = video_service.feedback_service.summarize_final_evaluation(
            output_feedback, exercise_type
        )

        print("Returning streaming response")
        return OutputPose(
            feedback=output_feedback,
        )
