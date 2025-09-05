from pydantic import BaseModel


class FeedbackComment(BaseModel):
    title: str
    feedback: str
    severity: str


class Feedback(BaseModel):
    exercise: str
    fixes: list[FeedbackComment]
    warnings: list[FeedbackComment]
    harmful: list[FeedbackComment]
