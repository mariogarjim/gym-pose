from enum import Enum


class ExerciseEnum(Enum):
    SQUAT = "squat"
    BENCH_PRESS = "bench_press"
    PULL_UP = "pull_up"


class ExerciseMeasureEnum(Enum):
    SQUAT_KNEE_ANKLE_ALIGNMENT = "squat_knee_ankle_alignment"
    SQUAT_DEPTH = "squat_depth"
    SQUAT_TORSO_ANGLE = "squat_torso_angle"
    HEAD_ALIGNMENT = "head_alignment"

    PULL_UP_ARMS_NEARLY_EXTENDED = "pull_up_arms_nearly_extended"
    PULL_UP_CHIN_OVER_BAR = "pull_up_chin_over_bar"
    PULL_UP_SHOULDER_ENGAGEMENT = "pull_up_shoulder_engagement"
    PULL_UP_BODY_CONTROL = "pull_up_body_control"

    def __str__(self):
        return self.value


class ExerciseFeedbackEnum(Enum):
    OPTIMAL = "optimal"
    IMPROVABLE = "improvable"
    HARMFUL = "harmful"

    def __str__(self):
        return self.value


class VideoFeedbackEnum(Enum):
    POSITIVE = "positive"
    IMPROVEMENT = "improvement"
    NEGATIVE = "negative"

    def __str__(self):
        return self.value
