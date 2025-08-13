import typing as t
from app.enum import (
    ExerciseEnum,
    ExerciseMeasureEnum,
    ExerciseFeedbackEnum,
    ExerciseRatingEnum,
)
from app.api.api_v2.schemas.exercise import ExerciseFeedback
from app.api.api_v2.schemas.feedback import Feedback, ImprovementPoint


class FeedbackService:
    def __init__(self):
        pass

    def summarize_final_evaluation(
        self,
        final_evaluation_feedbacks: t.List[dict[ExerciseMeasureEnum, ExerciseFeedback]],
        exercise: ExerciseEnum,
        show_all: bool = False,
    ) -> Feedback:
        overall_score = 80
        previous_scores = [70, 80, 81, 75]

        positive_feedback = []
        improvement_feedback = []
        for final_evaluation_feedback in final_evaluation_feedbacks:
            for measure, feedback_value in final_evaluation_feedback.items():
                if feedback_value.rating == ExerciseRatingEnum.PERFECT:
                    positive_feedback.append(feedback_value.comment)

                    if show_all:
                        improvement_point = ImprovementPoint(
                            title=measure.value,
                            feedback=feedback_value.comment,
                            severity=feedback_value.rating.value,
                        )
                        improvement_feedback.append(improvement_point)
                else:
                    improvement_point = ImprovementPoint(
                        title=measure.value,
                        feedback=feedback_value.comment,
                        severity=feedback_value.rating.value,
                    )
                    improvement_feedback.append(improvement_point)

        return Feedback(
            exercise=exercise,
            overall_score=overall_score,
            good_points=positive_feedback,
            improvement_points=improvement_feedback,
            previous_scores=previous_scores,
        )

    def generate_feedback(
        self,
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback],
        positive_feedback: list[ExerciseFeedback],
        improvement_feedback: list[ExerciseFeedback],
        negative_feedback: list[ExerciseFeedback],
    ) -> Feedback:
        improvement_points = []

        print("feedback", feedback)
        print("positive_feedback", positive_feedback)
        print("improvement_feedback", improvement_feedback)
        print("negative_feedback", negative_feedback)

        positive_feedback = []
        for pos_fed in positive_feedback:
            positive_feedback.append(feedback[pos_fed].comment)
            # Only for testing purposes
            improvement_points.append(
                title=feedback[pos_fed].feedback,
                feedback=feedback[pos_fed].comment,
                severity=ExerciseFeedbackEnum.IMPROVABLE.value,
            )

        for imp_fed in improvement_feedback:
            improvement_points.append(
                title=feedback[imp_fed].feedback,
                feedback=feedback[imp_fed].comment,
                severity=ExerciseFeedbackEnum.IMPROVABLE.value,
            )

        for neg_fed in negative_feedback:
            improvement_points.append(
                title=feedback[neg_fed].feedback,
                feedback=feedback[neg_fed].comment,
                severity=ExerciseFeedbackEnum.HARMFUL.value,
            )

        # Only for testing
        overall_score = 80
        previous_scores = [70, 80, 81]

        return Feedback(
            exercise=ExerciseEnum.SQUAT,
            overall_score=overall_score,
            good_points=positive_feedback,
            improvement_points=improvement_points,
            previous_scores=previous_scores,
        )
