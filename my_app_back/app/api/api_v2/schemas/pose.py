from pydantic import BaseModel
from app.api.api_v2.schemas.feedback import Feedback


class OutputPose(BaseModel):
    feedback: Feedback
