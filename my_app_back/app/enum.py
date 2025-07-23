from enum import Enum


class Exercise(Enum):
    SQUAT = "squat"


class ExerciseMeasure(Enum):
    SQUAT_KNEE_ALIGNMENT = "squat_knee_alignment"
    SQUAT_DEPTH = "squat_depth"
    SQUAT_TORSO_ANGLE = "squat_torso_angle"

    def __str__(self):
        return self.value


class ExercisePerformance(Enum):
    OPTIMAL = "optimal"
    IMPROVABLE = "improvable"
    HARMFUL = "harmful"

    def __str__(self):
        return self.value
