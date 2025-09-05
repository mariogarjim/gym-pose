import json
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict

import boto3
from app.api.api_v2.services.pose_evaluation import PoseEvaluationService
from app.enum import ExerciseEnum


class AnalysisStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda worker function triggered by SQS messages from S3 events.
    Processes video files uploaded to S3 and performs pose analysis.
    """

    print(f"Lambda function started with event: {json.dumps(event)}")
    print(
        f"Environment variables: BUCKET={os.environ.get('BUCKET')}, TABLE={os.environ.get('TABLE')}"
    )

    try:
        pose_evaluation_service = PoseEvaluationService()
        print("✓ PoseEvaluationService initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PoseEvaluationService: {e}")
        raise e

    s3_client = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")

    table_name = os.environ["TABLE"]
    table = dynamodb.Table(table_name)

    try:
        # Process each SQS record
        for record in event["Records"]:
            # Parse S3 event from SQS message
            s3_event = json.loads(record["body"])

            if "Records" in s3_event:
                for s3_record in s3_event["Records"]:
                    bucket = s3_record["s3"]["bucket"]["name"]
                    key = s3_record["s3"]["object"]["key"]
                    user_id = key.split("/")[1]
                    exercise_type = key.split("/")[2]
                    try:
                        exercise_type = ExerciseEnum(exercise_type)
                        print(f"exercise_type: {exercise_type}")
                    except ValueError:
                        raise ValueError(f"Invalid exercise type: {exercise_type}")

                    print(f"Processing video: {bucket}/{key}")

                    # TODO: Implement actual video processing logic
                    # 1. Download video from S3
                    # 2. Run pose analysis using MediaPipe/OpenCV
                    # 3. Generate results and feedback
                    # 4. Upload results back to S3
                    # 5. Update DynamoDB with analysis results

                    # Placeholder: Update DynamoDB with processing status
                    table.update_item(
                        Key={
                            "userId": user_id,
                            "exerciseType-date": f"{exercise_type}-{datetime.now().strftime('%Y-%m-%d')}",
                        },
                        UpdateExpression="set #s = :s",
                        ExpressionAttributeNames={"#s": "status"},
                        ExpressionAttributeValues={
                            ":s": AnalysisStatus.PROCESSING.value,
                        },
                    )

                    # Stream from S3 -> /tmp (constant memory)
                    tmp_path = f"/tmp/{uuid.uuid4().hex}{os.path.splitext(key)[1]}"
                    with open(tmp_path, "wb") as f:
                        s3_client.download_fileobj(bucket, key, f)

                    # Call the pose evaluation service
                    output_pose = pose_evaluation_service.evaluate_pose(
                        file_path=tmp_path,
                        exercise_type=exercise_type,
                        user_id=user_id,
                    )

                    feedback = output_pose.feedback

                    table.update_item(
                        Key={
                            "pk": f"user#{user_id}",
                            "sk": f"exercise#{exercise_type}",
                        },
                        UpdateExpression="set #s = :s, #f = :f",
                        ExpressionAttributeNames={"#s": "status", "#f": "feedback"},
                        ExpressionAttributeValues={
                            ":s": AnalysisStatus.DONE.value,
                            ":f": feedback.model_dump_json(),
                        },
                    )

        return {"statusCode": 200, "body": json.dumps("Successfully processed videos")}

    except Exception as e:
        print(f"Error processing videos: {str(e)}")
        raise e
