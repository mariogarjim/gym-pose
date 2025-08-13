import json
from openai import OpenAI
from typing import Optional, Dict, Any

from app.core.config import settings
from app.prompts import PROMPT_SYSTEM_FEEDBACK
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
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

    def generate_feedback_llm(
        self, feedback: Dict[str, Any], model: str = "gpt-4o-mini"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate feedback using OpenAI's API.

        Args:
            feedback (Dict[str, Any]): The feedback data to process
            model (str): The OpenAI model to use. Defaults to 'gpt-4o-mini'

        Returns:
            Optional[Dict[str, Any]]: The API response or None if there's an error

        Raises:
            Exception: If there's an error during the API call
        """
        try:
            print("feedback_test: ", str(feedback))

            # Convert feedback to a serializable format
            serializable_feedback = {}
            for key, value in feedback.items():
                if hasattr(value, "__dict__"):
                    serializable_feedback[str(key)] = {
                        "feedback": value.feedback,
                        "comment": value.comment,
                        "relevant_windows": [
                            {
                                "from_frame": w.from_frame,
                                "to_frame": w.to_frame,
                                "number_of_relevant_frames": w.number_of_relevant_frames,
                                "comment": w.comment,
                            }
                            for w in value.relevant_windows
                        ]
                        if value.relevant_windows
                        else [],
                    }
                else:
                    serializable_feedback[str(key)] = value

            feedback_str = json.dumps(serializable_feedback)
            print("feedback_str: ", feedback_str)

            response = self.client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT_SYSTEM_FEEDBACK,
                    },
                    {"role": "user", "content": feedback_str},
                ],
                temperature=0.0,
                response_format=FeedbackResponse,
            )

            print("response_test: ", str(response.choices[0].message.parsed))

            return response.choices[0].message.parsed

        except Exception as e:
            print(f"Error generating feedback: {str(e)}")
            return None

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
