import typing as t
import zipfile
import io
import json
from fastapi import APIRouter, File, Form, status
from fastapi.responses import StreamingResponse
from fastapi import UploadFile

from app.api.api_v2.api.dependencies.services import PoseEvaluationServiceDep
from app.api.api_v2.services.pose_evaluation import PoseEvaluationService
from app.api.api_v2.schemas.pose import OutputPose
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
def upload_video(
    files: t.List[UploadFile] = File(...),
    exercise_type: ExerciseEnum = Form(...),
    user_id: str = Form(...),
    pose_evaluation_service: PoseEvaluationService = PoseEvaluationServiceDep,
):
    """
    Upload and analyze multiple video files for exercise form assessment.

    Returns:
        StreamingResponse with processed videos and analysis

    Raises:
        HTTPException: If file upload or processing fails
    """
    # Convert multiple UploadFiles to a single ZIP BytesIO for the service
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            # Read file content
            file_content = file.file.read()
            # Write content to zip using writestr (not write)
            zip_file.writestr(file.filename, file_content)

    # Reset buffer position to beginning
    zip_buffer.seek(0)

    # Get the pose evaluation result
    pose_result = pose_evaluation_service.evaluate_pose(
        file_content=zip_buffer.read(),
        user_id=user_id,
        exercise_type=exercise_type,
    )

    # Create a new ZIP that includes both videos and feedback
    final_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(final_zip_buffer, "w", zipfile.ZIP_DEFLATED) as final_zip:
        # Add the processed videos ZIP
        final_zip.writestr("videos.zip", pose_result.videos)

        # Add feedback as JSON
        feedback_json = pose_result.feedback.model_dump()
        final_zip.writestr("feedback.json", json.dumps(feedback_json, indent=2))

    final_zip_buffer.seek(0)

    # Return the complete result as a streaming response
    return StreamingResponse(
        final_zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=analysis_result.zip"},
    )
