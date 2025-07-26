import json
from openai import OpenAI
from typing import Optional, Dict, Any

from app.core.config import settings


class Feedback:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

    def generate_feedback(
        self, feedback: Dict[str, Any], model: str = "gpt-4o-mini"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate feedback using OpenAI's API.

        Args:
            feedback (Dict[str, Any]): The feedback data to process
            model (str): The OpenAI model to use. Defaults to 'gpt-4-turbo-preview'

        Returns:
            Optional[Dict[str, Any]]: The API response or None if there's an error

        Raises:
            Exception: If there's an error during the API call
        """
        try:
            print("feedback_test: ", str(feedback))
            feedback_str = json.dumps(str(feedback))

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful fitness assistant providing feedback on exercise form. Add emojis in your answer!",
                    },
                    {"role": "user", "content": feedback_str},
                ],
                temperature=0.0,
            )

            print("response_test: ", str(response.choices[0].message.content))

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating feedback: {str(e)}")
            return None
