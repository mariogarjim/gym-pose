import typing as t
import numpy as np
import mediapipe as mp
from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExerciseFeedbackEnum
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
        feedback: ExerciseFeedbackEnum,
        comment: str = "",
    ):
        self.feedback = feedback.value
        self.comment = comment

    def __str__(self):
        return f"ExerciseFeedback(feedback={self.feedback}, comment={self.comment})"

    def __repr__(self):
        return self.__str__()


class RelevantFeedbackWindow:
    def __init__(
        self,
        window: t.Dict[ExerciseMeasureEnum, ExerciseFeedback],
        measure: ExerciseMeasureEnum,
        from_frame: int,
        to_frame: int,
        number_of_relevant_frames: int,
        exercise_feedback: ExerciseFeedback,
    ):
        self.window = window
        self.measure = measure
        self.from_frame = from_frame
        self.to_frame = to_frame
        self.number_of_relevant_frames = number_of_relevant_frames
        self.exercise_feedback = exercise_feedback

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
        self.deep_squad = False
        self.deepest_squad = 9999
        self.deepest_frame = 0
        self.head_alignment = [0] * self.total_frames

        # Temporal windows parameters
        self.window_size = 30
        self.window_threshold_frames = 10

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

        back_posture_angle = draw_back_posture(frame_img, shoulder, hip, torso_vec)
        if back_posture_angle > 40:
            self.back_posture[frame] = 1

        # [SQUAD-02] Squad depth:
        depth = hip[1] - knee[1]
        draw_squad_depth(frame_img, hip, knee, depth)
        if depth > 0:
            self.deep_squad = True

        # [SQUAD-03] Head alignment:
        horizontal_offset = ear[0] - shoulder[0]  # +ve = ear ahead of shoulder
        max_offset = 0.1
        # draw_head_alignment(frame_img, ear, shoulder, max_offset)
        if horizontal_offset > max_offset:
            self.head_alignment[frame] = 1

        print("########################")
        print("Frame: ", frame)
        print("Back_posture: ", self.back_posture[frame])
        print(
            f"Depth: {depth}. Deep_squad:  {self.deep_squad}. Deepest_frame: {self.deepest_frame}"
        )
        print(
            f"Horizontal_offset: {horizontal_offset}. Max_offset: {max_offset}. Head_alignment: {self.head_alignment[frame]}"
        )
        print("Back posture vector: ", self.back_posture)
        print("Head alignment vector: ", self.head_alignment)
        print("########################")

    def get_feedback_based_on_temporal_window(
        self,
        number_of_windows: int,
        measure: ExerciseMeasureEnum,
        measure_feedback: t.List[int],
    ) -> t.List[RelevantFeedbackWindow]:
        relevant_windows = []
        for window_index in range(number_of_windows):
            current_window_start = window_index * self.window_size
            current_window_end = current_window_start + self.window_size
            window = measure_feedback[current_window_start:current_window_end]

            relevant_frames = np.sum(window)
            if relevant_frames >= self.window_threshold_frames:
                relevant_windows.append(
                    RelevantFeedbackWindow(
                        window=window,
                        measure=measure.value,
                        from_frame=current_window_start,
                        to_frame=current_window_end,
                        number_of_relevant_frames=relevant_frames,
                        exercise_feedback=ExerciseFeedback(
                            feedback=ExerciseFeedbackEnum.HARMFUL,
                            comment=f"The {measure.value} is harmful from frames {current_window_start} to {current_window_end}",
                        ),
                    )
                )

        return relevant_windows

    def summarize_feedback(self) -> t.Dict[ExerciseMeasureEnum, ExerciseFeedback]:
        feedback = {}

        if not self.deep_squad:
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.IMPROVABLE,
                comment="The squat is not deep enough",
            )
        else:
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.IMPROVABLE,
                comment="The squat is deep enough",
            )

        print(
            "feedback[ExerciseMeasureEnum.SQUAT_DEPTH]: ",
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH],
        )

        number_of_windows = self.total_frames // self.window_size

        squat_torso_angle_feedback = self.get_feedback_based_on_temporal_window(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.SQUAT_TORSO_ANGLE,
            measure_feedback=self.back_posture,
        )
        if squat_torso_angle_feedback:
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE] = squat_torso_angle_feedback
        else:
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="The back posture is optimal",
            )

        print(
            "feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE]: ",
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE],
        )

        head_alignment_feedback = self.get_feedback_based_on_temporal_window(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.HEAD_ALIGNMENT,
            measure_feedback=self.head_alignment,
        )

        if head_alignment_feedback:
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT] = head_alignment_feedback
        else:
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="The head alignment is optimal",
            )

        print(
            "feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT]: ",
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT],
        )

        return feedback
