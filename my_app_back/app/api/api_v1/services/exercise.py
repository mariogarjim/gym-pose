import typing as t
import numpy as np
import mediapipe as mp
from app.enum import Exercise, ExerciseMeasure, ExercisePerformance
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList


class ExerciseFeedback:
    def __init__(
        self,
        values: t.Dict[str, float],
        performance: ExercisePerformance,
        frame: int,
        feedback: str = "",
    ):
        self.values = values
        self.performance = performance
        self.frame = frame
        self.feedback = feedback


def calculate_angle(a, b, c):
    try:
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        # Ensure the cosine value is within valid range [-1, 1]
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.arccos(cosine_angle)
        return float(np.degrees(angle))
    except Exception as e:
        print(f"Error calculating angle: {e}")
        print(f"Points: a={a}, b={b}, c={c}")
        return 0.0


def check_exercise_frame(
    exercise: Exercise,
    landmarks: NormalizedLandmarkList,
    frame: int,
    measures: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Dict[ExerciseMeasure, ExerciseFeedback]:
    if not measures:
        measures = {}
        for measure in ExerciseMeasure:
            measures[measure] = []

    # Considered error due to pixel size
    error_threshold = 0.05

    if exercise == Exercise.SQUAT:
        # Get landmark coordinates using landmark indices
        left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        left_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        ]
        left_ear = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_EAR.value]

        # Convert landmarks to points for angle calculation
        hip = [float(left_hip.x), float(left_hip.y)]
        knee = [float(left_knee.x), float(left_knee.y)]
        ankle = [float(left_ankle.x), float(left_ankle.y)]
        shoulder = [float(left_shoulder.x), float(left_shoulder.y)]
        ear = [float(left_ear.x), float(left_ear.y)]

        # [SQUAD-01] Hip-Knee-Ankle Alignment:
        if knee[0] > ankle[0] + error_threshold:
            measures[ExerciseMeasure.SQUAT_KNEE_ALIGNMENT].append(
                ExerciseFeedback(
                    values={"knee_x": knee[0], "ankle_x": ankle[0]},
                    performance=ExercisePerformance.POOR,
                    frame=frame,
                    feedback="The knee (KNEE) should not move far forward past the ankle (ANKLE) along the horizontal (X) axis.",
                )
            )

        # [SQUAD-02] Back Posture:
        # Define a line going down from the hip
        torso_angle = calculate_angle(shoulder, hip, knee)
        values = {"torso_angle": torso_angle}
        if torso_angle > 20 and torso_angle <= 45:
            measures[ExerciseMeasure.SQUAT_TORSO_ANGLE].append(
                ExerciseFeedback(
                    values=values,
                    performance=ExercisePerformance.IMPROVABLE,
                    frame=frame,
                    feedback="The torso leans forward moderately — aim to keep it more upright for better balance and posture.",
                )
            )
        elif torso_angle > 45:
            measures[ExerciseMeasure.SQUAT_TORSO_ANGLE].append(
                ExerciseFeedback(
                    values=values,
                    performance=ExercisePerformance.HARMFUL,
                    frame=frame,
                    feedback="The back is leaning too far forward, which increases stress on the spine and knees.",
                )
            )

        # [SQUAD-03] Squad depth:
        if hip[1] >= knee[1] + error_threshold:
            measures[ExerciseMeasure.SQUAT_DEPTH].append(
                ExerciseFeedback(
                    values={"hip_y": hip[1], "knee_y": knee[1]},
                    performance=ExercisePerformance.OPTIMAL,
                    frame=frame,
                    feedback="The hip joint drops at least to the same level as the knee joint (i.e., 'parallel') or below it ('deep squat').",
                )
            )

        # [SQUAD-04] Head alignment:
        horizontal_offset = ear[0] - shoulder[0]  # +ve = ear ahead of shoulder
        if horizontal_offset > 0.04:
            measures[ExerciseMeasure.SQUAT_HEAD_ALIGNMENT].append(
                ExerciseFeedback(
                    values={},
                    performance=ExercisePerformance.HARMFUL,
                    frame=frame,
                    feedback="The head (ear) should not tilt excessively forward to maintain the natural curvature of the spine.",
                )
            )

    return measures


"""
def evaluate_exercise(
    exercise: Exercise,
    measures: t.Dict[ExerciseMeasure, ExerciseFeedback],
    total_frames: int,
) -> t.Dict[ExerciseMeasure, ExerciseFeedback]:
    window_end = 30
    window_threshold_frames = 10
    window_start = 0
    window_size = window_end
    while window_end < total_frames:
        window_start += window_size
        window_end += window_size

    return measures
"""
