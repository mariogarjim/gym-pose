from enum import Enum


class Exercise(Enum):
    DEADLIFT = "deadlift"


class ExerciseMeasure(Enum):
    DEADLIFT_DEPTH = "deadlift_depth"
    DEADLIFT_KNEE_ALIGNMENT = "deadlift_knee_alignment"
    DEADLIFT_TORSO_ANGLE = "deadlift_torso_angle"
