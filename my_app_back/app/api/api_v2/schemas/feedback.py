from pydantic import BaseModel

from app.enum import ExerciseEnum


class ImprovementPoint(BaseModel):
    title: str
    feedback: str
    severity: str


class Feedback(BaseModel):
    exercise: ExerciseEnum
    overall_score: int
    good_points: list[str]
    improvement_points: list[ImprovementPoint]
    previous_scores: list[int]
