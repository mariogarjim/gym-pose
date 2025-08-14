import typing as t
from fastapi import APIRouter, File, Form, status
from fastapi.responses import StreamingResponse
from fastapi import UploadFile

from app.api.api_v2.api.dependencies.services import PoseEvaluationServiceDep
from app.api.api_v2.services.pose_evaluation import PoseEvaluationService
from app.api.api_v2.schemas.video import VideoMetadata
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
    video_files_metadata: t.Optional[t.List[VideoMetadata]] = Form(None),
    pose_evaluation_service: PoseEvaluationService = PoseEvaluationServiceDep,
):
    """
    Upload and analyze multiple video files for exercise form assessment.

    Returns:
        StreamingResponse with processed videos and analysis

    Raises:
        HTTPException: If file upload or processing fails
    """
    return await pose_evaluation_service.evaluate_pose(
        files=video_files,
        exercise_type=exercise_type,
        video_files_metadata=video_files_metadata,
    )
