import numpy as np
import mediapipe as mp
from app.enum import Exercise, ExerciseMeasure
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList


class ExerciseMeasureOutput:
    def __init__(self, formula: str, values: list[float], ok: bool):
        self.formula = formula
        self.values = values
        self.ok = ok


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


def measure_exercise(
    exercise: Exercise, landmarks: NormalizedLandmarkList
) -> list[ExerciseMeasureOutput]:
    measures = {}

    if exercise == Exercise.DEADLIFT:
        # Get landmark coordinates using landmark indices
        left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        left_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        ]

        # Convert landmarks to points for angle calculation
        hip = [float(left_hip.x), float(left_hip.y)]
        knee = [float(left_knee.x), float(left_knee.y)]
        ankle = [float(left_ankle.x), float(left_ankle.y)]
        shoulder = [float(left_shoulder.x), float(left_shoulder.y)]

        # Depth: The hips go below the knees
        measures[ExerciseMeasure.DEADLIFT_DEPTH] = ExerciseMeasureOutput(
            "$left_hip.y$ > $left_knee.y$",
            [float(left_hip.y), float(left_knee.y)],
            float(left_hip.y) >= float(left_knee.y),
        )

        # Knee alignment: Knees do not cave inward
        knee_angle = calculate_angle(hip, knee, ankle)
        measures[ExerciseMeasure.DEADLIFT_KNEE_ALIGNMENT] = ExerciseMeasureOutput(
            "$knee_angle$ < 90",
            [knee_angle],
            knee_angle < 90,
        )

        # Check torso angle
        torso_angle = calculate_angle(shoulder, hip, knee)
        measures[ExerciseMeasure.DEADLIFT_TORSO_ANGLE] = ExerciseMeasureOutput(
            "$torso_angle$ > 140",
            [torso_angle],
            torso_angle > 140,
        )

    return measures
