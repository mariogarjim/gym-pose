import typing as t
from fastapi import UploadFile
from pydantic import BaseModel

from app.enum import ExerciseEnum, Viewpoint


class VideoMetadata(BaseModel):
    viewpoint: str
