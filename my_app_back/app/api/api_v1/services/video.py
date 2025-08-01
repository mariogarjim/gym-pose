import io
import os
import tempfile
from zipfile import ZipFile

import cv2
import numpy as np
from app.enum import ExerciseMeasureEnum


class VideoService:
    def __init__(self):
        pass

    def _encode_frames_to_video(
        self, frames: list[np.ndarray], fps: int, extra_name: str
    ) -> bytes:
        if not frames:
            return None
        height, width, _ = frames[0].shape
        temp_fd, temp_path = tempfile.mkstemp(suffix=f"_{extra_name}.mp4")
        os.close(temp_fd)
        out = cv2.VideoWriter(
            temp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )
        for frame in frames:
            out.write(frame)
        out.release()
        return temp_path

    def _create_zip_with_videos(
        self, output_path: str, relevant_video_paths: list[str]
    ) -> io.BytesIO:
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_archive:
            zip_archive.write(output_path, arcname=os.path.basename(output_path))
            for idx, path in enumerate(relevant_video_paths):
                zip_archive.write(path, arcname=f"relevant_clip_{idx + 1}.mp4")
        zip_buffer.seek(0)
        return zip_buffer

    def process_relevant_videos(
        self,
        relevant_videos: dict[ExerciseMeasureEnum, list[np.ndarray]],
        fps: int,
    ) -> io.BytesIO:
        zip_buffer = None
        temp_video_paths = []

        output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
        os.close(output_fd)
        zip_buffer = self._create_zip_with_videos(
            output_path=output_path, relevant_video_paths=temp_video_paths
        )

        for measure, frames in relevant_videos.items():
            video_path = self._encode_frames_to_video(frames, fps, measure.value)
            if video_path:
                temp_video_paths.append(video_path)

            output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
            os.close(output_fd)
            zip_buffer = self._create_zip_with_videos(
                output_path=output_path, relevant_video_paths=temp_video_paths
            )
            zip_buffer.seek(0)

        return zip_buffer
