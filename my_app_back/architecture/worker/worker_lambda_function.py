import json
import boto3
import os
from typing import Dict, Any

from app.api.api_v2.services.pose_evaluation import PoseEvaluationService
from app.enum import ExerciseEnum
from enum import Enum


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

    bucket_name = os.environ["BUCKET"]
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
                    response = table.put_item(
                        Item={
                            "pk": f"video#{key}",
                            "sk": f"user#{user_id}",
                            "status": AnalysisStatus.PROCESSING.value,
                            "bucket": bucket,
                            "key": key,
                            "timestamp": context.aws_request_id,
                        }
                    )

                    # Get the file in memory
                    object = s3_client.get_object(Bucket=bucket, Key=key)
                    file_content = object["Body"].read()

                    # Call the pose evaluation service
                    output_pose = pose_evaluation_service.evaluate_pose(
                        file_content=file_content,
                        exercise_type=exercise_type,
                        user_id=user_id,
                    )

                    # table.update_item(
                    #    Key={"pk": f"video#{key}", "sk": f"user#{user_id}"},
                    #    UpdateExpression="set #s = :s, result_key = :r, result_url = :u",
                    #    ExpressionAttributeNames={"#s": "status"},
                    #    ExpressionAttributeValues={
                    #        ":s": AnalysisStatus.DONE.value,
                    #        ":r": output_pose.key,
                    #        ":u": output_pose.url,
                    #    },
                    # )

        return {"statusCode": 200, "body": json.dumps("Successfully processed videos")}

    except Exception as e:
        print(f"Error processing videos: {str(e)}")
        raise e
