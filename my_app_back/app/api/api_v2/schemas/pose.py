from pydantic import BaseModel


class OutputPose(BaseModel):
    key: str
    url: str
