import typing as t
import numpy as np
import mediapipe as mp
from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExercisePerformanceEnum
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from app.constants import MAPPING_EXERCISE_TO_EXERCISE_MEASURE
from app.utils import calculate_angle
from app.api.api_v1.services.draw import (
    draw_back_posture,
    draw_squad_depth,
    draw_head_alignment,
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


class ExerciseFactory:
    @staticmethod
    def get_exercise_strategy(exercise: ExerciseEnum):
        if exercise == ExerciseEnum.SQUAT:
            return ExerciseSquad
        else:
            raise ValueError(f"Exercise {exercise} not supported")


class BaseExercise:
    def __init__(self, exercise: ExerciseEnum, total_frames: int):
        self.exercise = exercise
        self.total_frames = total_frames

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
        error_threshold: float,
    ):
        raise NotImplementedError("Subclasses must implement this method")

    def summarize_feedback(self):
        raise NotImplementedError("Subclasses must implement this method")


class ExerciseSquad(BaseExercise):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.SQUAT, total_frames)

        self.back_posture = [0] * self.total_frames
        self.depth_squad = False
        self.head_alignment = [0] * self.total_frames

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
        error_threshold: float = 0.05,
    ):
        # Get landmark coordinates using landmark indices
        left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        ]
        left_ear = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_EAR.value]

        # Convert landmarks to points for angle calculation
        hip = [float(left_hip.x), float(left_hip.y)]
        knee = [float(left_knee.x), float(left_knee.y)]
        shoulder = [float(left_shoulder.x), float(left_shoulder.y)]
        ear = [float(left_ear.x), float(left_ear.y)]

        # [SQUAD-01] Back Posture:
        # Define a line going down from the hip
        torso_vec = np.array(hip) - np.array(shoulder)

        self.back_posture[frame] = draw_back_posture(
            frame_img, shoulder, hip, torso_vec
        )
        if self.back_posture[frame] > 40:
            self.back_posture[frame] = 1

        # [SQUAD-02] Squad depth:
        # draw_squad_depth(frame_img, hip, knee)
        if hip[1] >= knee[1] + error_threshold:
            self.depth_squad = True

        # [SQUAD-03] Head alignment:
        horizontal_offset = ear[0] - shoulder[0]  # +ve = ear ahead of shoulder
        max_offset = frame_img.shape[1] * 0.04
        # draw_head_alignment(frame_img, ear, shoulder, max_offset)
        if horizontal_offset > max_offset:
            self.head_alignment[frame] = 1

    def summarize_feedback(self) -> t.Dict[ExerciseMeasureEnum, ExerciseFeedback]:
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
