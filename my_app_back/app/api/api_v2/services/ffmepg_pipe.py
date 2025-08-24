# ffmpeg_pipe_writer.py
import subprocess
import numpy as np
import cv2
import os
import shutil
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
        # Check if ffmpeg is available
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError(
                "FFmpeg is not installed or not found in PATH. "
                "Please install FFmpeg to use video processing features.\n"
                "Installation instructions:\n"
                "- macOS: brew install ffmpeg\n"
                "- Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "- Windows: Download from https://ffmpeg.org/download.html"
            )

        # Use AWS credential chain: IAM roles in AWS, profiles locally
        env_profile = os.getenv("AWS_PROFILE")

        if env_profile:
            # Local development with explicit profile
            print(f"🏠 FFmpeg local dev: Using AWS profile: {env_profile}")
            session = boto3.Session(profile_name=env_profile)
            self.s3 = session.client("s3")
        else:
            # AWS environment: Use IAM roles automatically
            print("☁️ FFmpeg AWS environment: Using IAM role credentials")
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
            print(
                f"Resizing frame from {frame_bgr.shape} to {self.width}x{self.height}"
            )
            frame_bgr = cv2.resize(frame_bgr, (self.width, self.height))
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        if self.proc and self.proc.stdin:
            self.proc.stdin.write(frame_rgb.tobytes())

    def close_and_upload(self):
        # Close the ffmpeg process
        if self.proc and self.proc.stdin:
            self.proc.stdin.close()
            self.proc.wait()

        local_path = self.out_path
        key = f"results/{Path(local_path).name}"

        try:
            # Upload to S3
            self.s3.upload_file(
                local_path, BUCKET_NAME, key, ExtraArgs={"ContentType": "video/mp4"}
            )
            print(f"Successfully uploaded {local_path} to s3://{BUCKET_NAME}/{key}")
        except Exception as e:
            print(f"Failed to upload {local_path} to S3: {str(e)}")
            print(f"Bucket: {BUCKET_NAME}, Key: {key}")
            # Don't raise the exception, just log it for now
            # You can change this behavior based on your requirements

        # Free space
        try:
            os.remove(local_path)
        except FileNotFoundError:
            pass
