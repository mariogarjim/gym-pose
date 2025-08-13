import numpy as np
from typing import Optional

from pydantic import BaseModel

from app.enum import ExerciseRatingEnum, ExerciseMeasureEnum


class VideoSegment(BaseModel):
    applies_to_full_video: bool = False
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    relevant_frame_count: Optional[int] = None


class ExerciseFeedback(BaseModel):
    rating: ExerciseRatingEnum
    comment: str
    video_segments: list[VideoSegment]


class FinalEvaluation(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    feedback: dict[ExerciseMeasureEnum, ExerciseFeedback]
    videos: dict[ExerciseMeasureEnum, list[np.ndarray]]
