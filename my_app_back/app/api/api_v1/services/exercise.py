import typing as t
import numpy as np
import mediapipe as mp
from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExerciseFeedbackEnum
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from app.utils import calculate_angle
from app.api.api_v1.services.draw import (
    draw_back_posture,
    draw_squad_depth,
    draw_head_alignment,
    draw_landmarks,
    draw_pullup_chin_over_bar,
    draw_pullup_shoulder_engagement,
    draw_pullup_arms_nearly_extended,
)


class RelevantFeedbackWindow:
    def __init__(
        self,
        from_frame: int,
        to_frame: int,
        number_of_relevant_frames: int,
        comment: str = "",
    ):
        self.from_frame = from_frame
        self.to_frame = to_frame
        self.number_of_relevant_frames = number_of_relevant_frames
        self.comment = comment


class ExerciseFeedback:
    def __init__(
        self,
        feedback: ExerciseFeedbackEnum,
        comment: str = "",
        relevant_windows: list[RelevantFeedbackWindow] = [],
    ):
        self.feedback = feedback.value
        self.comment = comment
        self.relevant_windows = relevant_windows

    def __str__(self):
        return f"ExerciseFeedback(feedback={self.feedback}, comment={self.comment}, relevant_windows={self.relevant_windows})"

    def __repr__(self):
        return self.__str__()


class SummarizedFeedback:
    def __init__(
        self,
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback],
        videos: dict[ExerciseMeasureEnum, list[np.ndarray]],
        positive_feedback: list[str],
        improvement_feedback: list[str],
        negative_feedback: list[str],
    ):
        self.feedback = feedback
        self.videos = videos
        self.positive_feedback = positive_feedback
        self.improvement_feedback = improvement_feedback
        self.negative_feedback = negative_feedback


class ExerciseFactory:
    @staticmethod
    def get_exercise_strategy(exercise: ExerciseEnum):
        if exercise == ExerciseEnum.SQUAT:
            return ExerciseSquad
        elif exercise == ExerciseEnum.BENCH_PRESS:
            return ExerciseBenchPress
        elif exercise == ExerciseEnum.PULL_UP:
            return ExercisePullUp
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
    ):
        raise NotImplementedError("Subclasses must implement this method")

    def summarize_feedback(self):
        raise NotImplementedError("Subclasses must implement this method")

    def get_relevant_feedback_windows(
        self,
        number_of_windows: int,
        measure: ExerciseMeasureEnum,
        measure_feedback: t.List[int],
        window_threshold_frames: int,
        comment: str,
    ) -> t.List[RelevantFeedbackWindow]:
        relevant_windows = []
        for window_index in range(number_of_windows):
            current_window_start = window_index * self.window_size
            current_window_end = current_window_start + self.window_size
            window = measure_feedback[current_window_start:current_window_end]

            relevant_frames = np.sum(window)
            if relevant_frames >= window_threshold_frames:
                relevant_windows.append(
                    RelevantFeedbackWindow(
                        from_frame=current_window_start,
                        to_frame=current_window_end,
                        number_of_relevant_frames=relevant_frames,
                        comment=comment,
                    )
                )

        return relevant_windows


class ExerciseSquad(BaseExercise):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.SQUAT, total_frames)

        self.back_posture = [0] * self.total_frames
        self.deep_squad = False
        self.deepest_squad = 9999
        self.deepest_frame = 0
        self.head_alignment = [0] * self.total_frames

        self.back_posture_drawn_frames = []
        self.deep_squad_drawn_frames = []
        self.head_alignment_drawn_frames = []

        self.positive_feedback = []
        self.improvement_feedback = []
        self.negative_feedback = []

        # Temporal windows parameters
        self.window_size = 30
        self.window_threshold_frames = 10

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
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

        copy_frame_img = frame_img.copy()
        back_posture_angle = draw_back_posture(copy_frame_img, shoulder, hip, torso_vec)
        self.back_posture_drawn_frames.append(copy_frame_img)
        if back_posture_angle > 40:
            self.back_posture[frame] = 1

        # [SQUAD-02] Squad depth:
        depth = hip[1] - knee[1]
        copy_frame_img = frame_img.copy()
        draw_squad_depth(copy_frame_img, hip, knee, depth)
        self.deep_squad_drawn_frames.append(copy_frame_img)
        if depth > 0:
            self.deep_squad = True

        # [SQUAD-03] Head alignment:
        horizontal_offset = ear[0] - shoulder[0]  # +ve = ear ahead of shoulder
        max_offset = 0.1
        copy_frame_img = frame_img.copy()
        draw_head_alignment(copy_frame_img, ear, shoulder, max_offset)
        self.head_alignment_drawn_frames.append(copy_frame_img)
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

    def summarize_feedback(
        self,
    ) -> SummarizedFeedback:
        feedback = {}
        videos = {}

        if not self.deep_squad:
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH.value] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.IMPROVABLE,
                comment="The squat is not deep enough",
            )
            self.improvement_feedback.append(
                ExerciseMeasureEnum.SQUAT_DEPTH.value,
            )
        else:
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH.value] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="The squat is deep enough",
            )
            self.positive_feedback.append(
                ExerciseMeasureEnum.SQUAT_DEPTH.value,
            )

        videos[ExerciseMeasureEnum.SQUAT_DEPTH.value] = self.deep_squad_drawn_frames
        print(
            "feedback[ExerciseMeasureEnum.SQUAT_DEPTH]: ",
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH.value],
        )

        number_of_windows = self.total_frames // self.window_size

        squat_torso_angle_feedback = super().get_relevant_feedback_windows(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.SQUAT_TORSO_ANGLE,
            measure_feedback=self.back_posture,
            window_threshold_frames=self.window_threshold_frames,
            comment="Not straight back during the movement is harmful",
        )
        if squat_torso_angle_feedback:
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE.value] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.HARMFUL,
                comment="Not straight back during the movement is harmful",
                relevant_windows=squat_torso_angle_feedback,
            )
            self.negative_feedback.append(
                ExerciseMeasureEnum.SQUAT_TORSO_ANGLE.value,
            )
        else:
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE.value] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="The back posture is optimal",
            )
            self.positive_feedback.append(
                ExerciseMeasureEnum.SQUAT_TORSO_ANGLE.value,
            )
        videos[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE.value] = (
            self.back_posture_drawn_frames
        )

        print(
            "feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE]: ",
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE.value],
        )

        head_alignment_feedback = super().get_relevant_feedback_windows(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.HEAD_ALIGNMENT,
            measure_feedback=self.head_alignment,
            window_threshold_frames=self.window_threshold_frames,
            comment="The head is not correctlyaligned with the spine during this video frames.",
        )

        if head_alignment_feedback:
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT.value] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.HARMFUL,
                comment="Not aligned head with the spine is harmful.",
                relevant_windows=head_alignment_feedback,
            )
            self.negative_feedback.append(
                ExerciseMeasureEnum.HEAD_ALIGNMENT.value,
            )
        else:
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT.value] = ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="The head alignment with the spine is optimal",
            )
            self.positive_feedback.append(
                ExerciseMeasureEnum.HEAD_ALIGNMENT.value,
            )
        videos[ExerciseMeasureEnum.HEAD_ALIGNMENT.value] = (
            self.head_alignment_drawn_frames
        )
        print(
            "feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT]: ",
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT.value],
        )

        return SummarizedFeedback(
            feedback=feedback,
            videos=videos,
            positive_feedback=self.positive_feedback,
            improvement_feedback=self.improvement_feedback,
            negative_feedback=self.negative_feedback,
        )


class ExerciseBenchPress(BaseExercise):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.BENCH_PRESS, total_frames)

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
    ):
        draw_landmarks(frame_img, landmarks)

    def summarize_feedback(self) -> SummarizedFeedback:
        feedback = {}

        return SummarizedFeedback(
            feedback=feedback,
            videos={},
            positive_feedback=[],
            improvement_feedback=[],
            negative_feedback=[],
        )


class ExercisePullUp(BaseExercise):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.PULL_UP, total_frames)

        self.chin_over_bar = [0] * self.total_frames
        self.body_control = [0] * self.total_frames
        self.shoulder_engagement = [0] * self.total_frames
        self.arms_nearly_extended = [0] * self.total_frames

        # Temporal windows parameters for feedback
        self.window_size = 30

        # Drawn frames
        self.chin_over_bar_drawn_frames = []
        self.shoulder_engagement_drawn_frames = []
        self.arms_nearly_extended_drawn_frames = []

        self.positive_feedback = []
        self.improvement_feedback = []
        self.negative_feedback = []

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
    ):
        # Get landmark coordinates using landmark indices
        left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        left_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        ]
        right_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value
        ]
        left_elbow = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        left_ear = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_EAR.value]
        left_mouth = landmarks.landmark[mp.solutions.pose.PoseLandmark.MOUTH_LEFT.value]
        left_index_finger = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_INDEX.value
        ]
        right_index_finger = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.RIGHT_INDEX.value
        ]

        # Convert landmarks to points for angle calculation
        right_hip = [float(right_hip.x), float(right_hip.y)]
        left_hip = [float(left_hip.x), float(left_hip.y)]
        left_shoulder = [float(left_shoulder.x), float(left_shoulder.y)]
        right_shoulder = [float(right_shoulder.x), float(right_shoulder.y)]
        left_elbow = [float(left_elbow.x), float(left_elbow.y)]
        left_wrist = [float(left_wrist.x), float(left_wrist.y)]
        left_ear = [float(left_ear.x), float(left_ear.y)]
        right_ear = [float(right_ear.x), float(right_ear.y)]
        left_mouth = [float(left_mouth.x), float(left_mouth.y)]
        left_index_finger = [
            float(left_index_finger.x),
            float(left_index_finger.y),
        ]
        right_index_finger = [
            float(right_index_finger.x),
            float(right_index_finger.y),
        ]

        # [PULLUP-01] Full range of motion:

        ## Botton (arms nearly extended)
        arms_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        if arms_angle > 160:
            self.arms_nearly_extended[frame] = 1
        copy_frame_img = frame_img.copy()
        draw_pullup_arms_nearly_extended(
            copy_frame_img,
            left_shoulder,
            left_elbow,
            left_wrist,
            arms_angle,
        )
        self.arms_nearly_extended_drawn_frames.append(copy_frame_img)

        ## Top (chin over bar)
        copy_frame_img = frame_img.copy()
        chin_over_bar = draw_pullup_chin_over_bar(
            copy_frame_img, left_index_finger, right_index_finger, left_mouth
        )
        self.chin_over_bar_drawn_frames.append(copy_frame_img)
        if chin_over_bar > 0:
            self.chin_over_bar[frame] = 1

        # [PULLUP-02] Shoulder Engagement
        copy_frame_img = frame_img.copy()
        left_shoulder_to_ear_distance, right_shoulder_to_ear_distance = (
            draw_pullup_shoulder_engagement(
                copy_frame_img, left_shoulder, left_ear, right_shoulder, right_ear
            )
        )
        self.shoulder_engagement_drawn_frames.append(copy_frame_img)
        offset = 10
        threshold = int(0.05 * frame_img.shape[0]) + offset
        if (
            left_shoulder_to_ear_distance < threshold
            or right_shoulder_to_ear_distance < threshold
        ):
            self.shoulder_engagement[frame] = 1

        print("########################")
        print("Frame: ", frame)
        print("Chin over bar: ", self.chin_over_bar[frame])
        print(
            f"Shoulder engagement: {self.shoulder_engagement[frame]}. Left shoulder to ear distance: {left_shoulder_to_ear_distance}. Right shoulder to ear distance: {right_shoulder_to_ear_distance}. Threshold: {threshold}"
        )
        print("########################")

    def summarize_feedback(self) -> SummarizedFeedback:
        trheshold_frames_arms_nearly_extended = 3
        threshold_frames_chin_over_bar = 3
        threshold_frames_shoulder_engagement = 10

        number_of_windows = self.total_frames // self.window_size

        feedback = {}
        videos = {}

        arms_nearly_extended_feedback = super().get_relevant_feedback_windows(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED,
            measure_feedback=self.arms_nearly_extended,
            window_threshold_frames=trheshold_frames_arms_nearly_extended,
            exercise_feedback=ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="For the down phase, the arms are correctly extended",
            ),
        )
        videos[ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED.value] = (
            self.arms_nearly_extended_drawn_frames
        )
        if arms_nearly_extended_feedback:
            feedback[ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED.value] = (
                arms_nearly_extended_feedback
            )
            self.positive_feedback.append(
                ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED.value,
            )
        else:
            feedback[ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED.value] = (
                ExerciseFeedback(
                    feedback=ExerciseFeedbackEnum.IMPROVABLE,
                    comment="For the down phase, the arms are not extended",
                )
            )
            self.improvement_feedback.append(
                ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED.value,
            )

        chin_over_bar_feedback = super().get_relevant_feedback_windows(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR,
            measure_feedback=self.chin_over_bar,
            window_threshold_frames=threshold_frames_chin_over_bar,
            exercise_feedback=ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.OPTIMAL,
                comment="For the up phase, the chin is correctly over the bar",
            ),
        )
        videos[ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR.value] = (
            self.chin_over_bar_drawn_frames
        )
        if chin_over_bar_feedback:
            feedback[ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR.value] = (
                ExerciseFeedback(
                    feedback=ExerciseFeedbackEnum.OPTIMAL,
                    comment="For the up phase, the chin is correctly over the bar",
                    relevant_windows=chin_over_bar_feedback,
                )
            )
            self.positive_feedback.append(
                ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR.value,
            )
        else:
            feedback[ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR.value] = (
                ExerciseFeedback(
                    feedback=ExerciseFeedbackEnum.IMPROVABLE,
                    comment="For the up phase, the chin is not over the bar",
                )
            )
            self.improvement_feedback.append(
                ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR.value,
            )

        shoulder_engagement_feedback = super().get_relevant_feedback_windows(
            number_of_windows=number_of_windows,
            measure=ExerciseMeasureEnum.PULL_UP_SHOULDER_ENGAGEMENT,
            measure_feedback=self.shoulder_engagement,
            window_threshold_frames=threshold_frames_shoulder_engagement,
            exercise_feedback=ExerciseFeedback(
                feedback=ExerciseFeedbackEnum.HARMFUL,
                comment="The shoulders are not engaged throughout the movement. The shoulders remain inactive and unstable, contributing to improper form and injury prevention.",
            ),
        )
        videos[ExerciseMeasureEnum.PULL_UP_SHOULDER_ENGAGEMENT.value] = (
            self.shoulder_engagement_drawn_frames
        )
        if shoulder_engagement_feedback:
            feedback[ExerciseMeasureEnum.PULL_UP_SHOULDER_ENGAGEMENT.value] = (
                shoulder_engagement_feedback
            )
            self.positive_feedback.append(
                ExerciseMeasureEnum.PULL_UP_SHOULDER_ENGAGEMENT.value,
            )
        else:
            feedback[ExerciseMeasureEnum.PULL_UP_SHOULDER_ENGAGEMENT.value] = (
                ExerciseFeedback(
                    feedback=ExerciseFeedbackEnum.OPTIMAL,
                    comment="Excellent shoulder engagement throughout the movement. The shoulders remain active and stable, contributing to proper form and injury prevention.",
                )
            )
            self.improvement_feedback.append(
                ExerciseMeasureEnum.PULL_UP_SHOULDER_ENGAGEMENT.value,
            )

        return SummarizedFeedback(
            feedback=feedback,
            videos=videos,
            positive_feedback=self.positive_feedback,
            improvement_feedback=self.improvement_feedback,
            negative_feedback=self.negative_feedback,
        )
