from pydantic import BaseModel


class VideoMetadata(BaseModel):
    viewpoint: str
