# ffmpeg_pipe_writer.py
import subprocess
import numpy as np
import cv2
import os
from pathlib import Path
import boto3
from app.constants import BUCKET_NAME


class FFmpegPipeWriter:
    """
    Stream raw RGB frames into ffmpeg (libx264). One instance per measure.
    Call write(frame_bgr) repeatedly, then close() to finalize.
    """

    def __init__(
        self,
        out_path: str,
        width: int,
        height: int,
        fps: int = 6,
        crf: int = 23,
        preset: str = "veryfast",
    ):
        self.s3 = boto3.client("s3")
        self.out_path = out_path
        self.width, self.height = width, height
        self.proc = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                f"{width}x{height}",
                "-r",
                str(fps),
                "-i",
                "pipe:0",
                "-vf",
                "format=yuv420p",  # broader player compatibility
                "-c:v",
                "libx264",
                "-preset",
                preset,  # speed/size tradeoff
                "-crf",
                str(crf),  # quality (lower = bigger/better)
                "-movflags",
                "+faststart",
                out_path,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def write(self, frame_bgr: np.ndarray):
        # Ensure size matches; resize if needed
        if frame_bgr.shape[1] != self.width or frame_bgr.shape[0] != self.height:
            frame_bgr = cv2.resize(frame_bgr, (self.width, self.height))
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        self.proc.stdin.write(frame_rgb.tobytes())

    def close_and_upload(self):
        local_path = self.out_path
        key = f"results/{Path(local_path).name}"

        # Upload to S3
        self.s3.upload_file(
            local_path, BUCKET_NAME, key, ExtraArgs={"ContentType": "video/mp4"}
        )

        # Free space
        try:
            os.remove(local_path)
        except FileNotFoundError:
            pass
