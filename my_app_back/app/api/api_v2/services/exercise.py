import typing as t

import mediapipe as mp
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
import uuid


from app.api.api_v1.services.exercise import (
    draw_back_posture,
    draw_head_alignment,
    draw_squad_depth,
    draw_pullup_chin_over_bar,
    draw_pullup_shoulder_engagement,
    draw_pullup_arms_nearly_extended,
    calculate_angle,
)
from app.api.api_v2.schemas.exercise import (
    ExerciseFeedback,
    VideoSegment,
)
from app.constants import (
    MAPPING_EXERCISE_MEASURE_TO_COMMENT,
    MAPPING_EXERCISE_TO_EXERCISE_MEASURES,
)
from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExerciseRatingEnum
from app.api.api_v2.services.ffmepg_pipe import FFmpegPipeWriter
from app.api.api_v2.services.calculation import CalculationService


"""
The fps of the feedback annotated videos are reduce to 6 fps to reduce costs.
This is enough to see the feedback, not very big visual difference.
"""

"""
There are different types of measures.
 - Measures that are independent to reps i.e. back posture: 
    Back posture should be correct during all the video.
 - Measures that are dependent to reps:
    1. Measures that are calculated at the start of the concentric phase 
        and at the end of the eccentric phase.
    2. Measures that are calculated once per repetition i.e. squat depth.
"""

""" 

Idea para el futuro:

Para asegurarnos que las mediciones entre frames tienen la minima cantidad de ruido posible,
utilizamos el filtro de Savitzky–Golay (truco local de aproximación polinómica).

La idea es que los movimientos de los ejercicios son curvas suaves en el tiempo, especialmente
en tiempos cortos. Por ello, cogemos conjuntos de n frames (i.e. 6 frames) y aproximamos ese
pequeño tramo con un polinomio de bajo grado (i.e. grado 2). Todos los puntos de cada 6 
frames se pasarán por este filtro, asegurándonos que la curva resultante es suave.
"""


class ExerciseFactory:
    @staticmethod
    def get_exercise_strategy_service(exercise_type: ExerciseEnum, total_frames: int):
        if exercise_type == ExerciseEnum.SQUAT:
            return ExerciseSquad(total_frames)
        elif exercise_type == ExerciseEnum.BENCH_PRESS:
            return ExerciseBenchPress(total_frames)
        elif exercise_type == ExerciseEnum.PULL_UP:
            return ExercisePullUp(total_frames)
        elif exercise_type == ExerciseEnum.SIDE_LATERAL_RAISE:
            return ExerciseSideLateralRaises(total_frames)
        else:
            raise ValueError(f"Exercise {exercise_type} not supported")


class BaseExerciseService:
    def __init__(self, exercise: ExerciseEnum, total_frames: int):
        self.exercise = exercise
        self.total_frames = total_frames

        # Default parameters for temporal evaluation
        self.window_size = 30
        self.window_threshold_frames = 10

        # FFmpeg writers for the feedback annotated videos
        self.writers: dict[ExerciseMeasureEnum, FFmpegPipeWriter] = {}

        self.calculation_service = CalculationService()

    def get_writer(
        self, measure: ExerciseMeasureEnum, w: int, h: int
    ) -> FFmpegPipeWriter:
        """
        Get the FFmpeg writer for the measure. If it doesn't exist, create it.
        """
        if measure in self.writers:
            return self.writers[measure]
        out_path = f"/tmp/{uuid.uuid4().hex}_{measure}.mp4"
        self.writers[measure] = FFmpegPipeWriter(
            out_path, w, h, fps=6, crf=22, preset="veryfast"
        )
        return self.writers[measure]

    def evaluate_frame(
        self,
        frame_img: np.ndarray,
        frame: int,
        landmarks: NormalizedLandmarkList,
    ):
        raise NotImplementedError("Subclasses must implement this method")

    def get_final_evaluation(self) -> dict[ExerciseMeasureEnum, ExerciseFeedback]:
        raise NotImplementedError("Subclasses must implement this method")


class ExerciseSquad(BaseExerciseService):
    def __init__(self, total_frames: int):
        exercise = ExerciseEnum.SQUAT
        super().__init__(exercise, total_frames)

        # Measures
        self.measures = MAPPING_EXERCISE_TO_EXERCISE_MEASURES[exercise]

        # Empty states to perform the feedback evaluation
        self.back_posture = np.zeros(self.total_frames, dtype=np.uint8)
        self.deep_squad_frames = 0
        self.head_alignment = np.zeros(self.total_frames, dtype=np.uint8)

    def set_relevant_landmark_points(self, landmarks: NormalizedLandmarkList):
        # Get landmark coordinates using landmark indices
        left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        left_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        ]
        left_ear = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_EAR.value]

        # Convert landmarks to points for angle calculation
        self.hip = [float(left_hip.x), float(left_hip.y)]
        self.knee = [float(left_knee.x), float(left_knee.y)]
        self.shoulder = [float(left_shoulder.x), float(left_shoulder.y)]
        self.ear = [float(left_ear.x), float(left_ear.y)]

    def annotate_frame(
        self,
        frame_img: np.ndarray,
        w: int,
        h: int,
        back_posture_angle_deg: int,
        depth: int,
        max_offset: int,
    ):
        copy_frame_back_posture = frame_img.copy()
        draw_back_posture(
            frame=copy_frame_back_posture,
            shoulder=self.shoulder,
            hip=self.hip,
            max_offset=max_offset,
        )
        copy_frame_squad_depth = frame_img.copy()
        draw_squad_depth(
            frame=copy_frame_squad_depth, knee=self.knee, hip=self.hip, depth=depth
        )
        copy_frame_head_alignment = frame_img.copy()
        draw_head_alignment(
            frame=copy_frame_head_alignment,
            ear=self.ear,
            shoulder=self.shoulder,
            max_offset=max_offset,
        )

        self.get_writer(ExerciseMeasureEnum.SQUAT_BACK_POSTURE, w, h).write(
            copy_frame_back_posture
        )
        self.get_writer(ExerciseMeasureEnum.SQUAT_DEPTH, w, h).write(
            copy_frame_squad_depth
        )
        self.get_writer(ExerciseMeasureEnum.HEAD_ALIGNMENT, w, h).write(
            copy_frame_head_alignment
        )

    def evaluate_frame(
        self, frame_img: np.ndarray, frame_index: int, landmarks: NormalizedLandmarkList
    ):
        self.set_relevant_landmark_points(landmarks)
        # #########################################################################
        # [SQUAD-01] Back Posture:
        # #########################################################################
        # Define a line going down from the hip
        back_posture_angle = self.calculation_service.squat_back_posture_calculations(
            self.shoulder, self.hip, frame_img.shape
        )
        if back_posture_angle > 40:
            self.back_posture[frame_index] = 1

        # #########################################################################
        # [SQUAD-02] Squad depth:
        # #########################################################################
        depth = self.calculation_service.squat_depth_calculations(
            self.hip, self.knee, frame_img.shape
        )
        if depth > 0:
            self.deep_squad_frames += 1

        # #########################################################################
        # [SQUAD-03] Head alignment:
        # #########################################################################
        horizontal_offset = self.calculation_service.squat_head_alignment_calculations(
            self.ear, self.shoulder, frame_img.shape
        )
        max_offset = 0.1
        if horizontal_offset > max_offset:
            self.head_alignment[frame_index] = 1

        # #########################################################################
        # Draw feedback. We only annotate every 5 frames to reduce the number of frames.
        # #########################################################################
        if frame_index % 5 == 0:
            self.annotate_frame(
                frame_img,
                w=frame_img.shape[1],
                h=frame_img.shape[0],
                back_posture_angle_deg=back_posture_angle,
                depth=depth,
                max_offset=horizontal_offset,
            )

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
    ) -> dict[ExerciseMeasureEnum, ExerciseFeedback]:
        # Upload all the videos to S3
        for _, writer in self.writers.items():
            writer.close_and_upload()

        # Get the feedback
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
            feedback[ExerciseMeasureEnum.SQUAT_BACK_POSTURE] = ExerciseFeedback(
                rating=ExerciseRatingEnum.DANGEROUS,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.SQUAT_BACK_POSTURE
                ][ExerciseRatingEnum.DANGEROUS],
                video_segments=squat_torso_angle_feedback,
            )
        else:
            feedback[ExerciseMeasureEnum.SQUAT_BACK_POSTURE] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.SQUAT][
                    ExerciseMeasureEnum.SQUAT_BACK_POSTURE
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

        return feedback


class ExerciseBenchPress(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.BENCH_PRESS, total_frames)

        # Drawed frames list
        self.videos: dict[ExerciseMeasureEnum, list[np.ndarray]] = {}
        for measure in MAPPING_EXERCISE_TO_EXERCISE_MEASURES[ExerciseEnum.BENCH_PRESS]:
            self.videos[measure] = []

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
    ):
        mp.solutions.drawing_utils.draw_landmarks(
            frame_img, landmarks, mp.solutions.pose.POSE_CONNECTIONS
        )
        self.videos[ExerciseMeasureEnum.BASIC_LANDMARKS].append(frame_img)

    def get_final_evaluation(self):
        dummy_feedback = {
            ExerciseMeasureEnum.BASIC_LANDMARKS: ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment="",
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )
        }
        return dummy_feedback


class ExercisePullUp(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.PULL_UP, total_frames)

        # Initial values for the feedback experimentation:
        self.shoulder_correct_position = [0] * self.total_frames
        self.chin_over_bar = [0] * self.total_frames
        self.arms_extended = [0] * self.total_frames

        # Drawed frames list
        self.videos: dict[ExerciseMeasureEnum, list[np.ndarray]] = {}
        for measure in MAPPING_EXERCISE_TO_EXERCISE_MEASURES[ExerciseEnum.PULL_UP]:
            self.videos[measure] = []

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
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
        self.videos[ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED].append(
            copy_frame_img
        )

        ## Top (chin over bar)
        copy_frame_img = frame_img.copy()
        chin_over_bar = draw_pullup_chin_over_bar(
            copy_frame_img, left_index_finger, right_index_finger, left_mouth
        )
        self.videos[ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR].append(copy_frame_img)
        if chin_over_bar > 0:
            self.chin_over_bar[frame] = 1

        # [PULLUP-02] Shoulder Engagement
        copy_frame_img = frame_img.copy()
        left_shoulder_to_ear_distance, right_shoulder_to_ear_distance = (
            draw_pullup_shoulder_engagement(
                copy_frame_img, left_shoulder, left_ear, right_shoulder, right_ear
            )
        )
        self.videos[ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION].append(
            copy_frame_img
        )
        offset = 10
        threshold = int(0.05 * frame_img.shape[0]) + offset
        if (
            left_shoulder_to_ear_distance < threshold
            or right_shoulder_to_ear_distance < threshold
        ):
            self.shoulder_correct_position[frame] = 1

        mp.solutions.drawing_utils.draw_landmarks(
            frame_img, landmarks, mp.solutions.pose.POSE_CONNECTIONS
        )

    def _get_relevant_video_segments(
        self,
        measure_feedback: t.List[int],
        window_threshold_frames: int = None,
    ) -> t.List[VideoSegment]:
        if window_threshold_frames is None:
            window_threshold_frames = self.window_threshold_frames

        number_of_windows = self.total_frames // self.window_size

        video_segments = []
        for window_index in range(number_of_windows):
            current_window_start = window_index * self.window_size
            current_window_end = current_window_start + self.window_size
            window = measure_feedback[current_window_start:current_window_end]

            relevant_frames = np.sum(window)
            if relevant_frames >= window_threshold_frames:
                video_segments.append(
                    VideoSegment(
                        applies_to_full_video=False,
                        start_frame=current_window_start,
                        end_frame=current_window_end,
                        relevant_frame_count=relevant_frames,
                    )
                )

        return video_segments

    def get_final_evaluation(self):
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback] = {}

        trheshold_frames_arms_extended = 3
        threshold_frames_chin_over_bar = 3
        threshold_frames_shoulder_correct_position = 10

        arms_extended_feedback = self._get_relevant_video_segments(
            measure_feedback=self.arms_extended,
            window_threshold_frames=trheshold_frames_arms_extended,
        )
        if arms_extended_feedback:
            feedback[ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.WARNING,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.PULL_UP][
                        ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED
                    ][ExerciseRatingEnum.WARNING],
                    video_segments=arms_extended_feedback,
                )
            )
        else:
            feedback[ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.PULL_UP][
                        ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED
                    ][ExerciseRatingEnum.PERFECT],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        chin_over_bar_feedback = self._get_relevant_video_segments(
            measure_feedback=self.chin_over_bar,
            window_threshold_frames=threshold_frames_chin_over_bar,
        )
        if chin_over_bar_feedback:
            feedback[ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.PULL_UP][
                    ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR
                ][ExerciseRatingEnum.PERFECT],
                video_segments=chin_over_bar_feedback,
            )
        else:
            feedback[ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR] = ExerciseFeedback(
                rating=ExerciseRatingEnum.WARNING,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.PULL_UP][
                    ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR
                ][ExerciseRatingEnum.WARNING],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )

        shoulder_correct_position_feedback = self._get_relevant_video_segments(
            measure_feedback=self.shoulder_correct_position,
            window_threshold_frames=threshold_frames_shoulder_correct_position,
        )

        if shoulder_correct_position_feedback:
            feedback[ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.DANGEROUS,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.PULL_UP][
                        ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION
                    ][ExerciseRatingEnum.DANGEROUS],
                    video_segments=shoulder_correct_position_feedback,
                )
            )
        else:
            feedback[ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[ExerciseEnum.PULL_UP][
                        ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION
                    ][ExerciseRatingEnum.PERFECT],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        return feedback


class ExerciseSideLateralRaises(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.SIDE_LATERAL_RAISE, total_frames)

        # Initial values for the feedback experimentation:
        self.arms_abduction_up_correct_position = [0] * self.total_frames
        self.arms_lifting_too_high = [0] * self.total_frames
        self.incorrect_elbows_bend_angles = [0] * self.total_frames
        self.left_shoulder_elevation_array = []
        self.right_shoulder_elevation_array = []
        self.incorrect_symmetry = [0] * self.total_frames

        # Drawed frames list
        self.videos: dict[ExerciseMeasureEnum, list[np.ndarray]] = {}
        for measure in MAPPING_EXERCISE_TO_EXERCISE_MEASURES[
            ExerciseEnum.SIDE_LATERAL_RAISE
        ]:
            self.videos[measure] = []

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
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
        right_elbow = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value
        ]
        left_wrist = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value
        ]

        # Convert landmarks to points for angle calculation
        right_hip = [float(right_hip.x), float(right_hip.y)]
        left_hip = [float(left_hip.x), float(left_hip.y)]
        left_shoulder = [float(left_shoulder.x), float(left_shoulder.y)]
        right_shoulder = [float(right_shoulder.x), float(right_shoulder.y)]
        left_elbow = [float(left_elbow.x), float(left_elbow.y)]
        right_elbow = [float(right_elbow.x), float(right_elbow.y)]
        left_wrist = [float(left_wrist.x), float(left_wrist.y)]
        right_wrist = [float(right_wrist.x), float(right_wrist.y)]

        # [SIDE_LATERAL_RAISE-01] Arms abduction not high enough or too high

        left_abduction_angle = calculate_angle(left_hip, left_shoulder, left_wrist)
        right_abduction_angle = calculate_angle(right_hip, right_shoulder, right_wrist)

        lifting_too_high = left_abduction_angle > 110 and right_abduction_angle > 110

        if lifting_too_high:
            self.arms_lifting_too_high[frame] = 1

        lifting_up_correct = (
            left_abduction_angle > 70 and right_abduction_angle > 70
        ) and not lifting_too_high

        if lifting_up_correct:
            self.arms_abduction_up_correct_position[frame] = 1

        # [SIDE_LATERAL_RAISE-02] Elbows bend angles

        left_elbow_bend_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_bend_angle = calculate_angle(
            right_shoulder, right_elbow, right_wrist
        )

        locked_elbow = left_elbow_bend_angle < 10 or right_elbow_bend_angle < 10
        too_much_elbow_bend = left_elbow_bend_angle > 40 or right_elbow_bend_angle > 40

        if locked_elbow or too_much_elbow_bend:
            self.incorrect_elbows_bend_angles[frame] = 1

        # [SIDE_LATERAL_RAISE-03] Shoulders incorrect elevation

        left_shoulder_elevation = left_shoulder[1] - left_hip[1]
        right_shoulder_elevation = right_shoulder[1] - right_hip[1]

        self.left_shoulder_elevation_array.append(left_shoulder_elevation)
        self.right_shoulder_elevation_array.append(right_shoulder_elevation)

        # [SIDE_LATERAL_RAISE-04] Symmetry

        symmetry = abs(left_abduction_angle - right_abduction_angle)
        if symmetry > 10:
            self.incorrect_symmetry[frame] = 1

        mp.solutions.drawing_utils.draw_landmarks(
            frame_img, landmarks, mp.solutions.pose.POSE_CONNECTIONS
        )
        self.videos[ExerciseMeasureEnum.BASIC_LANDMARKS].append(frame_img)
        self.videos[
            ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH
        ].append(frame_img)
        self.videos[
            ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION
        ].append(frame_img)
        self.videos[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES].append(
            frame_img
        )
        self.videos[
            ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION
        ].append(frame_img)
        self.videos[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY].append(frame_img)

    def get_final_evaluation(self):
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback] = {}

        generic_threshold_frames = 10
        too_high_threshold_frames = 5

        # Check if the arms are lifting up correctly
        if np.sum(self.arms_lifting_too_high) > too_high_threshold_frames:
            feedback[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.DANGEROUS,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.SIDE_LATERAL_RAISE
                    ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH][
                        ExerciseRatingEnum.DANGEROUS
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )
        else:
            feedback[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.SIDE_LATERAL_RAISE
                    ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH][
                        ExerciseRatingEnum.PERFECT
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        # Arms correct abduction
        if np.sum(self.arms_abduction_up_correct_position) <= generic_threshold_frames:
            feedback[
                ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION
            ] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                    ExerciseEnum.SIDE_LATERAL_RAISE
                ][
                    ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION
                ][ExerciseRatingEnum.PERFECT],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )
        else:
            feedback[
                ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION
            ] = ExerciseFeedback(
                rating=ExerciseRatingEnum.WARNING,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                    ExerciseEnum.SIDE_LATERAL_RAISE
                ][
                    ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION
                ][ExerciseRatingEnum.WARNING],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )

        # Check if the elbows are bending correctly
        if np.sum(self.incorrect_elbows_bend_angles) > generic_threshold_frames:
            feedback[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.WARNING,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.SIDE_LATERAL_RAISE
                    ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES][
                        ExerciseRatingEnum.WARNING
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )
        else:
            feedback[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.SIDE_LATERAL_RAISE
                    ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES][
                        ExerciseRatingEnum.PERFECT
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        # Check if the shoulders are elevated correctly
        average_ten_lowest_elevations = np.mean(
            np.sort(self.left_shoulder_elevation_array)[:10]
        )
        average_ten_highest_elevations = np.mean(
            np.sort(self.left_shoulder_elevation_array)[-10:]
        )
        baseline_elevation = average_ten_highest_elevations * 0.05

        if (
            abs(average_ten_lowest_elevations - average_ten_highest_elevations)
            < baseline_elevation
        ):
            feedback[
                ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION
            ] = ExerciseFeedback(
                rating=ExerciseRatingEnum.DANGEROUS,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                    ExerciseEnum.SIDE_LATERAL_RAISE
                ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION][
                    ExerciseRatingEnum.DANGEROUS
                ],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )
        else:
            feedback[
                ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION
            ] = ExerciseFeedback(
                rating=ExerciseRatingEnum.PERFECT,
                comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                    ExerciseEnum.SIDE_LATERAL_RAISE
                ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION][
                    ExerciseRatingEnum.PERFECT
                ],
                video_segments=[VideoSegment(applies_to_full_video=True)],
            )

        # Check if the body is symmetrical
        if np.sum(self.incorrect_symmetry) > generic_threshold_frames:
            feedback[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.DANGEROUS,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.SIDE_LATERAL_RAISE
                    ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY][
                        ExerciseRatingEnum.DANGEROUS
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )
        else:
            feedback[ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.SIDE_LATERAL_RAISE
                    ][ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY][
                        ExerciseRatingEnum.PERFECT
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        return feedback


class ExerciseTricepsExtension(BaseExerciseService):
    def __init__(self, total_frames: int):
        super().__init__(ExerciseEnum.TRICEPS_EXTENSION, total_frames)

        # Initial values for the feedback experimentation:
        self.complete_up_extension = [0] * self.total_frames
        self.complete_down_extension = [0] * self.total_frames
        self.shoulder_angle = []

    def evaluate_frame(
        self, frame_img: np.ndarray, frame: int, landmarks: NormalizedLandmarkList
    ):
        # Get landmark coordinates using landmark indices
        left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        left_shoulder = landmarks.landmark[
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        ]
        left_elbow = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]

        # Convert landmarks to points for angle calculation
        left_hip = [float(left_hip.x), float(left_hip.y)]
        left_shoulder = [float(left_shoulder.x), float(left_shoulder.y)]
        left_elbow = [float(left_elbow.x), float(left_elbow.y)]
        left_wrist = [float(left_wrist.x), float(left_wrist.y)]

        # [TRICEPS_EXTENSION-01] Arms abduction not high enough or too high

        elbow_extension_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        if elbow_extension_angle > 170:
            self.complete_up_extension[frame] = 1
        if elbow_extension_angle < 80:
            self.complete_down_extension[frame] = 1

        # [TRICEPS_EXTENSION-02] Shoulder angle
        shoulder_angle = calculate_angle(left_hip, left_shoulder, left_elbow)

        self.shoulder_angle.append(shoulder_angle)

        mp.solutions.drawing_utils.draw_landmarks(
            frame_img, landmarks, mp.solutions.pose.POSE_CONNECTIONS
        )
        self.videos[ExerciseMeasureEnum.BASIC_LANDMARKS].append(frame_img)
        self.videos[ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION].append(
            frame_img
        )
        self.videos[
            ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION
        ].append(frame_img)
        self.videos[ExerciseMeasureEnum.TRICEPS_EXTENSION_SHOULDER_ANGLE].append(
            frame_img
        )

    def get_final_evaluation(self):
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback] = {}

        full_extension_threshold = 3

        # Check if the arms are extending correctly
        if np.sum(self.complete_up_extension) > full_extension_threshold:
            feedback[ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.TRICEPS_EXTENSION
                    ][ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION][
                        ExerciseRatingEnum.PERFECT
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )
        else:
            feedback[ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.WARNING,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.TRICEPS_EXTENSION
                    ][ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION][
                        ExerciseRatingEnum.WARNING
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        # Check if the arms are flexing correctly
        if np.sum(self.complete_down_extension) > full_extension_threshold:
            feedback[ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.TRICEPS_EXTENSION
                    ][ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION][
                        ExerciseRatingEnum.PERFECT
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )
        else:
            feedback[ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.WARNING,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.TRICEPS_EXTENSION
                    ][ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION][
                        ExerciseRatingEnum.WARNING
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        # Check if the shoulder angle is correct

        # Sorted shoulder angles
        sorted_shoulder_angles = np.sort(self.shoulder_angle)

        # Average of the 10 lowest shoulder angles
        average_ten_lowest_shoulder_angles = np.mean(sorted_shoulder_angles[:10])

        # Average of the 10 highest shoulder angles
        average_ten_highest_shoulder_angles = np.mean(sorted_shoulder_angles[-10:])

        difference_between_lowest_and_highest_shoulder_angles = (
            average_ten_highest_shoulder_angles - average_ten_lowest_shoulder_angles
        )

        if difference_between_lowest_and_highest_shoulder_angles > 10:
            feedback[ExerciseMeasureEnum.TRICEPS_EXTENSION_SHOULDER_ANGLE] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.DANGEROUS,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.TRICEPS_EXTENSION
                    ][ExerciseMeasureEnum.TRICEPS_EXTENSION_SHOULDER_ANGLE][
                        ExerciseRatingEnum.DANGEROUS
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )
        else:
            feedback[ExerciseMeasureEnum.TRICEPS_EXTENSION_SHOULDER_ANGLE] = (
                ExerciseFeedback(
                    rating=ExerciseRatingEnum.PERFECT,
                    comment=MAPPING_EXERCISE_MEASURE_TO_COMMENT[
                        ExerciseEnum.TRICEPS_EXTENSION
                    ][ExerciseMeasureEnum.TRICEPS_EXTENSION_SHOULDER_ANGLE][
                        ExerciseRatingEnum.PERFECT
                    ],
                    video_segments=[VideoSegment(applies_to_full_video=True)],
                )
            )

        return feedback
