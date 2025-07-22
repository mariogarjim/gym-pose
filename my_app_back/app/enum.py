from enum import Enum


class Exercise(Enum):
    SQUAT = "squat"


class ExerciseMeasure(Enum):
    SQUAT_KNEE_ALIGNMENT = "squat_knee_alignment"
    SQUAT_DEPTH = "squat_depth"
    SQUAT_TORSO_ANGLE = "squat_torso_angle"

    def __str__(self):
        return self.value


class ExerciseMeasureResult(Enum):
    OPTIMAL = "optimal"
    ADEQUATE = "adequate"
    POOR = "poor"

    def __str__(self):
        return self.value
