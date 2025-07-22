import typing as t
import numpy as np
import mediapipe as mp
from app.enum import Exercise, ExerciseMeasure, ExerciseMeasureResult
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList


class ExerciseMeasurement:
    def __init__(self, values: t.Dict[str, float], ok: ExerciseMeasureResult):
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
    exercise: Exercise,
    landmarks: NormalizedLandmarkList,
    result: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Dict[ExerciseMeasure, ExerciseMeasurement]:
    if not result:
        measures = {}
        for measure in ExerciseMeasure:
            measures[measure] = []

    error_threshold = 0.05

    if exercise == Exercise.SQUAT:
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

        key_point_values = {
            "hip": hip,
            "knee": knee,
            "ankle": ankle,
            "shoulder": shoulder,
        }

        # [SQUAD-01] Hip-Knee-Ankle Alignment:
        if knee[0] > ankle[0] + error_threshold:
            measures[ExerciseMeasure.SQUAT_KNEE_ALIGNMENT].append(
                ExerciseMeasurement(
                    values={},
                    ok=ExerciseMeasureResult.OPTIMAL
                    if knee[0] > ankle[0] + error_threshold
                    else ExerciseMeasureResult.POOR,
                )
            )

        # [SQUAD-02] Back Posture:

        # Define a line going down from the hip
        hip_to_knee_line = [hip[0], knee[0], hip[1], knee[1]]
        torso_angle = calculate_angle(shoulder, hip, hip_to_knee_line)
        values = {"torso_angle": torso_angle, "hip_to_knee_line": hip_to_knee_line}
        if torso_angle > 0 and torso_angle <= 20:
            measures[ExerciseMeasure.SQUAT_TORSO_ANGLE].append(
                ExerciseMeasurement(
                    values=values,
                    ok=ExerciseMeasureResult.OPTIMAL,
                )
            )
        elif torso_angle > 20 and torso_angle <= 45:
            measures[ExerciseMeasure.SQUAT_TORSO_ANGLE].append(
                ExerciseMeasurement(
                    values=values,
                    ok=ExerciseMeasureResult.ADEQUATE,
                )
            )
        else:
            measures[ExerciseMeasure.SQUAT_TORSO_ANGLE].append(
                ExerciseMeasurement(
                    values=values,
                    ok=ExerciseMeasureResult.POOR,
                )
            )

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
