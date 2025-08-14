from typing import Annotated
from fastapi import Depends
from app.api.api_v2.services.video import VideoService
from app.api.api_v2.services.feedback import FeedbackService
from app.api.api_v2.services.pose_evaluation import PoseEvaluationService


def get_feedback_service() -> FeedbackService:
    """Dependency for feedback service."""
    return FeedbackService()


FeedbackServiceDep = Depends(get_feedback_service)


def get_video_service(
    feedback_service: FeedbackService = FeedbackServiceDep,
) -> VideoService:
    """
    Dependency provider for VideoService.

    Args:
        feedback_service: Injected feedback service

    Returns:
        Configured VideoService instance
    """
    return VideoService(feedback_service=feedback_service)


VideoServiceDep = Depends(get_video_service)


def get_pose_evaluation_service() -> PoseEvaluationService:
    """Dependency for pose evaluation service."""
    return PoseEvaluationService()


PoseEvaluationServiceDep = Depends(get_pose_evaluation_service)
