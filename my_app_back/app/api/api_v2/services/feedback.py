import typing as t
from app.enum import (
    ExerciseEnum,
    ExerciseMeasureEnum,
    ExerciseRatingEnum,
)
from app.api.api_v2.schemas.exercise import ExerciseFeedback
from app.api.api_v2.schemas.feedback import Feedback


class FeedbackService:
    def __init__(self):
        pass

    def summarize_final_evaluation(
        self,
        final_evaluation_feedbacks_list: t.List[
            dict[ExerciseMeasureEnum, ExerciseFeedback]
        ],
        exercise_type: ExerciseEnum,
        show_all: bool = True,
    ) -> Feedback:
        feedback = Feedback(
            exercise=exercise_type.value,
            fixes=[],  # TODO: Insert values
            warnings=[],
            harmful=[],
        )

        for final_evaluation_feedback in final_evaluation_feedbacks_list:
            for measure, feedback_value in final_evaluation_feedback.items():
                if feedback_value.rating == ExerciseRatingEnum.WARNING:
                    feedback.warnings.append(
                        title=measure.value,
                        feedback=feedback_value.comment,
                        severity=feedback_value.rating.value,
                    )
                elif feedback_value.rating == ExerciseRatingEnum.DANGEROUS:
                    feedback.harmful.append(
                        title=measure.value,
                        feedback=feedback_value.comment,
                        severity=feedback_value.rating.value,
                    )

        return feedback
