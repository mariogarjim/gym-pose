import io
import json
import logging
import os
import tempfile
import traceback

import cv2
import mediapipe as mp
from app.api.api_v1.services import ExerciseFactory, Feedback, VideoService
from app.enum import ExerciseEnum
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    exercise_type: ExerciseEnum = Query(...),
    drawn_all: bool = Query(False),
) -> StreamingResponse:
    """
    Upload and process a video file.
    Returns a StreamingResponse with the processed video and feedback in headers.
    """
    feedback_service = Feedback()
    video_service = VideoService()
    exercise_strategy = ExerciseFactory.get_exercise_strategy(exercise_type)
    mp_pose = mp.solutions.pose

    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Temporal file to save the uploaded video
    input_fd, input_path = tempfile.mkstemp(suffix=".mp4")
    os.close(input_fd)

    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Failed to open uploaded video")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    exercise = exercise_strategy(total_frames)

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
                exercise.evaluate_frame(
                    frame_img=frame,
                    frame=frame_count,
                    landmarks=landmarks,
                    drawn_all=drawn_all,
                )

            frame_count += 1

    cap.release()

    summarized_feedback = exercise.summarize_feedback()
    exercise_feedback = summarized_feedback.feedback
    relevant_videos = summarized_feedback.relevant_videos

    feedback_text = ""
    # generated_feedback = feedback_service.generate_feedback(
    #    feedback=exercise_feedback,
    # )
    feedback_json = json.dumps(feedback_text)
    print("feedback_json_test ", feedback_json)

    # Return processed video with feedback in headers
    zip_buffer = video_service.process_relevant_videos(
        relevant_videos=relevant_videos, fps=fps
    )
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="processed_{file.filename}_response.zip"',
            "X-Exercise-Feedback": feedback_json,
            "clips_generated": str(len(relevant_videos.keys())),
        },
    )
