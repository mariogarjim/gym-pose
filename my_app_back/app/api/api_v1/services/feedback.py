from pydantic import BaseModel, Field
from app.enum import ExerciseMeasureEnum, ExerciseFeedbackEnum, ExerciseEnum
from app.api.api_v1.services.exercise import ExerciseFeedback


class ExerciseMeasurementFeedback(BaseModel):
    feedback: str = Field(description="Feedback for the exercise measure")
    type: str = Field(description="Type of feedback")

    def __str__(self):
        return (
            f"ExerciseMeasurementFeedback(feedback={self.feedback}, type={self.type})"
        )

    def __repr__(self):
        return self.__str__()


class FeedbackResponse(BaseModel):
    general_feedback: str = Field(
        description="General feedback for the complete exercise"
    )
    exercise_measurement_feedback: list[ExerciseMeasurementFeedback] = Field(
        description="Feedback for each exercise measure"
    )

    def __str__(self):
        return f"FeedbackResponse(general_feedback={self.general_feedback}, exercise_measurement_feedback={self.exercise_measurement_feedback})"

    def __repr__(self):
        return self.__str__()


class ImprovementPoint(BaseModel):
    title: str
    feedback: str
    severity: str


class FeedbackDict(BaseModel):
    exercise: ExerciseEnum
    overall_score: int
    good_points: list[str]
    improvement_points: list[ImprovementPoint]
    previous_scores: list[int]


class Feedback:
    def __init__(self):
        pass

    def generate_feedback(
        self,
        feedback: dict[ExerciseMeasureEnum, ExerciseFeedback],
        positive_feedback: list[ExerciseFeedback],
        improvement_feedback: list[ExerciseFeedback],
        negative_feedback: list[ExerciseFeedback],
    ) -> FeedbackDict:
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

        return FeedbackDict(
            exercise=ExerciseEnum.SQUAT,
            overall_score=overall_score,
            good_points=positive_feedback,
            improvement_points=improvement_points,
            previous_scores=previous_scores,
        )
