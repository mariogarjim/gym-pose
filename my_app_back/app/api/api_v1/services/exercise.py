import typing as t
import numpy as np
import mediapipe as mp
from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExercisePerformanceEnum
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from app.constants import MAPPING_EXERCISE_TO_EXERCISE_MEASURE
from app.utils import calculate_angle
from app.api.api_v1.services.draw import (
    draw_hip_and_knee_lines,
    draw_back_posture,
    draw_knee_ankle_alignment,
)


class ExerciseFeedback:
    def __init__(
        self,
        values: t.Dict[str, float],
        performance: ExercisePerformanceEnum,
        frame: int,
        feedback: str = "",
    ):
        self.values = values
        self.performance = performance
        self.frame = frame
        self.feedback = feedback


class RelevantFeedbackWindow:
    def __init__(
        self,
        window: t.Dict[ExerciseMeasureEnum, ExerciseFeedback],
        measure: ExerciseMeasureEnum,
        from_frame: int,
        to_frame: int,
        number_of_relevant_frames: int,
    ):
        self.window = window
        self.measure = measure
        self.from_frame = from_frame
        self.to_frame = to_frame
        self.number_of_relevant_frames = number_of_relevant_frames

    def __str__(self):
        return f"RelevantFeedbackWindow(measure={self.measure}, from_frame={self.from_frame}, to_frame={self.to_frame}, number_of_relevant_frames={self.number_of_relevant_frames})"

    def __repr__(self):
        return self.__str__()


class Exercise:
    def __init__(
        self,
        exercise: ExerciseEnum,
        total_frames: int,
    ):
        self.exercise = exercise
        self.total_frames = total_frames
        self.feedback = [{}] * total_frames

    def evaluate_exercise_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
    ) -> t.Dict[ExerciseMeasureEnum, ExerciseFeedback]:
        # Considered error due to pixel size
        error_threshold = 0.05

        if self.exercise == ExerciseEnum.SQUAT:
            # Get landmark coordinates using landmark indices
            left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
            left_knee = landmarks.landmark[
                mp.solutions.pose.PoseLandmark.LEFT_KNEE.value
            ]
            left_ankle = landmarks.landmark[
                mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value
            ]
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

            # [SQUAD-01] Back Posture:
            # Define a line going down from the hip
            torso_angle = calculate_angle(shoulder, hip, knee)
            draw_back_posture(
                frame_img,
                shoulder,
                hip,
            )
            values = {"torso_angle": torso_angle}
            if torso_angle > 20 and torso_angle <= 45:
                self.feedback[frame][ExerciseMeasureEnum.SQUAT_TORSO_ANGLE] = (
                    ExerciseFeedback(
                        values=values,
                        performance=ExercisePerformanceEnum.IMPROVABLE,
                        frame=frame,
                        feedback="The torso leans forward moderately — aim to keep it more upright for better balance and posture.",
                    )
                )
            elif torso_angle > 45:
                self.feedback[frame][ExerciseMeasureEnum.SQUAT_TORSO_ANGLE] = (
                    ExerciseFeedback(
                        values=values,
                        performance=ExercisePerformanceEnum.HARMFUL,
                        frame=frame,
                        feedback="The back is leaning too far forward, which increases stress on the spine and knees.",
                    )
                )

            # [SQUAD-02] Squad depth:
            draw_hip_and_knee_lines(frame_img, hip, knee)
            if hip[1] >= knee[1] + error_threshold:
                self.feedback[frame][ExerciseMeasureEnum.SQUAT_DEPTH] = (
                    ExerciseFeedback(
                        values={"hip_y": hip[1], "knee_y": knee[1]},
                        performance=ExercisePerformanceEnum.OPTIMAL,
                        frame=frame,
                        feedback="You achieved a deep squat! Keep it up!",
                    )
                )

            # [SQUAD-03] Head alignment:
            horizontal_offset = ear[0] - shoulder[0]  # +ve = ear ahead of shoulder
            # draw_head_alignment(frame_img, ear, shoulder)
            if horizontal_offset > 0.04:
                self.feedback[frame][ExerciseMeasureEnum.HEAD_ALIGNMENT] = (
                    ExerciseFeedback(
                        values={},
                        performance=ExercisePerformanceEnum.HARMFUL,
                        frame=frame,
                        feedback="The head should not tilt excessively forward to maintain the natural curvature of the spine.",
                    )
                )

    def evaluate_exercise(self) -> t.Dict[ExerciseMeasureEnum, ExerciseFeedback]:
        window_size = 30
        window_threshold_frames = 10

        number_of_windows = self.total_frames // window_size

        relevant_window_per_measure = {}

        for exercise_measure in MAPPING_EXERCISE_TO_EXERCISE_MEASURE[self.exercise]:
            relevant_windows = []
            for window_index in range(number_of_windows):
                current_window_start = window_index * window_size
                current_window_end = current_window_start + window_size
                window = self.feedback[current_window_start:current_window_end]

                relevant_frames = 0
                for frame in window:
                    if exercise_measure in frame:
                        relevant_frames += 1

                if relevant_frames >= window_threshold_frames:
                    relevant_windows.append(
                        RelevantFeedbackWindow(
                            window=window,
                            measure=exercise_measure,
                            from_frame=current_window_start,
                            to_frame=current_window_end,
                            number_of_relevant_frames=relevant_frames,
                        )
                    )

            relevant_window_per_measure[exercise_measure] = relevant_windows

        print(relevant_window_per_measure)

        return relevant_window_per_measure
