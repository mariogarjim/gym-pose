import os
import tempfile
from typing import BinaryIO

import cv2
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
import mediapipe as mp
from app.api.api_v1.services.exercise import measure_exercise
from app.enum import Exercise


router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def iterfile(file_like: BinaryIO):
    while chunk := file_like.read(8192):
        yield chunk


@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Temporal file to save the uploaded video
        input_fd, input_path = tempfile.mkstemp(suffix=".mp4")
        os.close(input_fd)

        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Temporal file to save the processed video
        output_fd, output_path = tempfile.mkstemp(suffix=".mp4")
        os.close(output_fd)

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Failed to open uploaded video")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # MediaPipe pose setup
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils

        with mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose:
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb_frame)
                landmarks = result.pose_landmarks

                if landmarks:
                    measures = measure_exercise(Exercise.SQUAT, landmarks)

                    if measures:
                        for i, (measure_name, measure_output) in enumerate(
                            measures.items()
                        ):
                            text = f"{measure_name.name}: {', '.join(f'{v:.1f}' for v in measure_output.values)} ({'OK' if measure_output.ok else 'X'})"
                            color = (0, 255, 0) if measure_output.ok else (0, 0, 255)

                            cv2.putText(
                                frame,
                                text,
                                (30, 40 + i * 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                color,
                                2,
                                cv2.LINE_AA,
                            )

                    mp_drawing.draw_landmarks(
                        frame,
                        landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(
                            color=(0, 255, 0), thickness=2, circle_radius=2
                        ),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                    )

                out.write(frame)
                frame_count += 1

        cap.release()
        out.release()

        # Return processed video
        video_file = open(output_path, "rb")
        return StreamingResponse(
            iterfile(video_file),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename}"
            },
        )
    except Exception as e:
        print(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary files
        if "input_path" in locals() and os.path.exists(input_path):
            os.remove(input_path)
        if "output_path" in locals() and os.path.exists(output_path):
            os.remove(output_path)
