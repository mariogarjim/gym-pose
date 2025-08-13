import typing as t
import json
from fastapi import APIRouter, Body, File, Form, status, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import UploadFile
from pydantic import ValidationError

from app.api.api_v2.api.dependencies.services import VideoServiceDep
from app.api.api_v2.schemas.video import VideoMetadata
from app.api.api_v2.services.video import VideoService
from app.enum import ExerciseEnum

router = APIRouter(
    prefix="/video",
    tags=["video"],
)


@router.post(
    "/upload",
    summary="Upload a video for processing",
    status_code=status.HTTP_201_CREATED,
    response_class=StreamingResponse,
)
async def upload_video(
    video_files: t.List[UploadFile] = File(...),
    exercise_type: ExerciseEnum = Form(...),
    video_metadata: t.Optional[t.List[VideoMetadata]] = Form(None),
    video_service: VideoService = VideoServiceDep,
):
    """
    Upload and analyze multiple video files for exercise form assessment.

    Returns:
        StreamingResponse with processed videos and analysis

    Raises:
        HTTPException: If file upload or processing fails
    """
    return await video_service.upload_and_process(
        files=video_files, exercise_type=exercise_type, video_metadata=video_metadata
    )
