import io
import os
import tempfile
from zipfile import ZipFile

import cv2
import numpy as np
from app.enum import VideoFeedbackEnum


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

    def process_videos(
        self,
        videos: dict[VideoFeedbackEnum, list[np.ndarray]],
        fps: int,
    ) -> io.BytesIO:
        root_dir_name = "videos"
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_archive:
            for feedback, videos in videos.items():
                for frames in videos:
                    video_path = self._encode_frames_to_video(frames, fps, feedback)
                    if video_path:
                        arcname = os.path.join(
                            root_dir_name, feedback.value, os.path.basename(video_path)
                        )
                    zip_archive.write(video_path, arcname=arcname)
                    os.remove(video_path)  # Cleanup temp video file

        zip_buffer.seek(0)
        return zip_buffer
