import typing as t

import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList

from app.api.api_v1.services.exercise import (
    draw_back_posture,
    draw_head_alignment,
    draw_squad_depth,
)
from app.api.api_v2.schemas.exercise import (
    ExerciseFeedback,
    FinalEvaluation,
    VideoSegment,
)
from app.constants import (
    MAPPING_EXERCISE_MEASURE_TO_COMMENT,
    MAPPING_EXERCISE_TO_EXERCISE_MEASURES,
)
from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExerciseRatingEnum


class ExerciseFactory:
    @staticmethod
    def get_exercise_strategy_service(exercise_type: ExerciseEnum, total_frames: int):
        if exercise_type == ExerciseEnum.SQUAT:
            return ExerciseSquad(total_frames)
        elif exercise_type == ExerciseEnum.BENCH_PRESS:
            return ExerciseBenchPress(total_frames)
        elif exercise_type == ExerciseEnum.PULL_UP:
            return ExercisePullUp(total_frames)
        else:
            raise ValueError(f"Exercise {exercise_type} not supported")


class BaseExerciseService:
    def __init__(self, exercise: ExerciseEnum, total_frames: int):
        self.exercise = exercise
        self.total_frames = total_frames

        # Temporal windows basic parameters
        self.window_size = 30
        self.window_threshold_frames = 10

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
    ):
        raise NotImplementedError("Subclasses must implement this method")

    def get_final_evaluation(self) -> FinalEvaluation:
        raise NotImplementedError("Subclasses must implement this method")


class ExerciseSquad(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.SQUAT, total_frames)

        # Initial values for the feedback experimentation:
        self.back_posture = [0] * self.total_frames
        self.deep_squad_frames = 0
        self.head_alignment = [0] * self.total_frames

        # Drawed frames list
        self.videos: dict[ExerciseMeasureEnum, list[np.ndarray]] = {}
        for measure in MAPPING_EXERCISE_TO_EXERCISE_MEASURES[ExerciseEnum.SQUAT]:
            self.videos[measure] = []

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
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
        self.videos[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE].append(copy_frame_img)
        if back_posture_angle > 40:
            self.back_posture[frame] = 1

        # [SQUAD-02] Squad depth:
        depth = hip[1] - knee[1]
        # Create a txt file with the depth and frame
        with open("depth.txt", "a") as f:
            f.write(f"depth: {depth} frame: {frame}\n")
        copy_frame_img = frame_img.copy()
        draw_squad_depth(copy_frame_img, hip, knee, depth, frame)
        self.videos[ExerciseMeasureEnum.SQUAT_DEPTH].append(copy_frame_img)
        if depth > 0:
            self.deep_squad_frames += 1

        # [SQUAD-03] Head alignment:
        horizontal_offset = ear[0] - shoulder[0]  # +ve = ear ahead of shoulder
        max_offset = 0.1
        copy_frame_img = frame_img.copy()
        draw_head_alignment(copy_frame_img, ear, shoulder, max_offset)
        self.videos[ExerciseMeasureEnum.HEAD_ALIGNMENT].append(copy_frame_img)
        if horizontal_offset > max_offset:
            self.head_alignment[frame] = 1

        # Draw landmarks
        mp.solutions.drawing_utils.draw_landmarks(
            frame_img, landmarks, mp.solutions.pose.POSE_CONNECTIONS
        )
        self.videos[ExerciseMeasureEnum.BASIC_LANDMARKS].append(frame_img)

    def _get_relevant_video_segments(
        self,
        measure_feedback: t.List[int],
    ) -> t.List[VideoSegment]:
        number_of_windows = self.total_frames // self.window_size

        video_segments = []
        for window_index in range(number_of_windows):
            current_window_start = window_index * self.window_size
            current_window_end = current_window_start + self.window_size
            window = measure_feedback[current_window_start:current_window_end]

            relevant_frames = np.sum(window)
            if relevant_frames >= self.window_threshold_frames:
                video_segments.append(
                    VideoSegment(
                        applies_to_full_video=False,
                        start_frame=current_window_start,
                        end_frame=current_window_end,
                        relevant_frame_count=relevant_frames,
                    )
                )

        return video_segments

    def get_final_evaluation(
        self,
    ) -> FinalEvaluation:
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback] = {}

        deep_squad_threshold = 30
        if self.deep_squad_frames < deep_squad_threshold:
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH] = ExerciseFeedback(
                rating=ExerciseRatingEnum.WARNING,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.SQUAT_DEPTH
                ][ExerciseRatingEnum.WARNING],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )
        else:
            feedback[ExerciseMeasureEnum.SQUAT_DEPTH] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.SQUAT_DEPTH
                ][ExerciseRatingEnum.PERFECT],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )

        squat_torso_angle_feedback = self._get_relevant_video_segments(
            measure_feedback=self.back_posture,
        )
        if squat_torso_angle_feedback:
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE] = ExerciseFeedback(
                rating=ExerciseRatingEnum.DANGEROUS,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.SQUAT_TORSO_ANGLE
                ][ExerciseRatingEnum.DANGEROUS],
                video_segments=squat_torso_angle_feedback,
            )
        else:
            feedback[ExerciseMeasureEnum.SQUAT_TORSO_ANGLE] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.SQUAT_TORSO_ANGLE
                ][ExerciseRatingEnum.PERFECT],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )

        head_alignment_feedback = self._get_relevant_video_segments(
            measure_feedback=self.head_alignment,
        )
        if head_alignment_feedback:
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT] = ExerciseFeedback(
                rating=ExerciseRatingEnum.DANGEROUS,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.HEAD_ALIGNMENT
                ][ExerciseRatingEnum.DANGEROUS],
                video_segments=head_alignment_feedback,
            )
        else:
            feedback[ExerciseMeasureEnum.HEAD_ALIGNMENT] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.HEAD_ALIGNMENT
                ][ExerciseRatingEnum.PERFECT],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )

        return FinalEvaluation(
            feedback=feedback,
            videos=self.videos,
        )


class ExerciseBenchPress(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.BENCH_PRESS, total_frames)

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
    ):
        pass

    def summarize_feedback(self):
        pass


class ExercisePullUp(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.PULL_UP)
        self.total_frames = total_frames

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
    ):
        pass

    def summarize_feedback(self):
        pass
