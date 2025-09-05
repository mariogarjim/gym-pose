from enum import Enum


class ExerciseEnum(Enum):
    SQUAT = "squat"
    BENCH_PRESS = "bench_press"
    PULL_UP = "pull_up"
    SIDE_LATERAL_RAISE = "side_lateral_raise"
    TRICEPS_EXTENSION = "triceps_extension"


class ExerciseMeasureEnum(Enum):
    BASIC_LANDMARKS = "basic_landmarks"

    # SQUAT
    SQUAT_KNEE_ANKLE_ALIGNMENT = "squat.knee_ankle_alignment"
    SQUAT_DEPTH = "squat.depth"
    SQUAT_BACK_POSTURE = "squat.back_posture"
    HEAD_ALIGNMENT = "head.alignment"

    # PULL UP
    PULL_UP_ARMS_NEARLY_EXTENDED = "pull_up.arms_nearly_extended"
    PULL_UP_CHIN_OVER_BAR = "pull_up.chin_over_bar"
    PULL_UP_SHOULDER_CORRECT_POSITION = "pull_up.shoulder_correct_position"

    # SIDE LATERAL RAISE
    SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH = (
        "side_lateral_raise.arms_lifting_too_high"
    )
    SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION = (
        "side_lateral_raise.arms_abduction_up_correct_position"
    )
    SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES = "side_lateral_raise.elbows_bend_angles"
    SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION = (
        "side_lateral_raise.shoulders_incorrect_elevation"
    )
    SIDE_LATERAL_RAISE_SYMMETRY = "side_lateral_raise.symmetry"

    # TRICEPS EXTENSION
    TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION = "triceps_extension.complete_up_extension"
    TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION = (
        "triceps_extension.complete_down_extension"
    )
    TRICEPS_EXTENSION_SHOULDER_ANGLE = "triceps_extension.shoulder_angle"

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
