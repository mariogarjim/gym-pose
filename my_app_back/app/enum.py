from enum import Enum


class ExerciseEnum(Enum):
    SQUAT = "squat"
    BENCH_PRESS = "bench_press"
    PULL_UP = "pull_up"


class ExerciseMeasureEnum(Enum):
    BASIC_LANDMARKS = "basic_landmarks"

    SQUAT_KNEE_ANKLE_ALIGNMENT = "squat_knee_ankle_alignment"
    SQUAT_DEPTH = "squat_depth"
    SQUAT_TORSO_ANGLE = "squat_torso_angle"
    HEAD_ALIGNMENT = "head_alignment"

    PULL_UP_ARMS_NEARLY_EXTENDED = "pull_up_arms_nearly_extended"
    PULL_UP_CHIN_OVER_BAR = "pull_up_chin_over_bar"
    PULL_UP_SHOULDER_CORRECT_POSITION = "pull_up_shoulder_correct_position"

    def __str__(self):
        return self.value


class ExerciseFeedbackEnum(Enum):
    OPTIMAL = "optimal"
    IMPROVABLE = "improvable"
    HARMFUL = "harmful"

    def __str__(self):
        return self.value


class Viewpoint(str, Enum):
    FRONT = "front"
    SIDE = "side"
    BACK = "back"


class ExerciseRatingEnum(Enum):
    PERFECT = "perfect"
    WARNING = "warning"
    DANGEROUS = "dangerous"
