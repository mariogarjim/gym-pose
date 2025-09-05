import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

import boto3

BUCKET = os.environ["BUCKET"]
DYNAMODB_TABLE = os.environ["TABLE"]
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Lambda function that handles HTTP requests from API Gateway.
    Provides endpoints for upload URLs, status checks, and results.
    """

    try:
        # Parse the request
        method = event.get("httpMethod", "")
        path = event.get("path", "")
        params = event.get("queryStringParameters") or {}

        print(f"Request: {method} {path}")

        # Route the request
        if method == "GET" and path == "/health":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"status": "healthy!"}),
            }

        elif method == "POST" and path == "/generate-presigned-url":
            user_id = params.get("user_id")
            filename = params.get("filename")
            exercise_type = params.get("exercise_type")

            if not user_id or not filename or not exercise_type:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {"error": "user_id, filename and exercise_type are required"}
                    ),
                }

            if "." in filename:
                base, ext = filename.rsplit(".", 1)
                ext = "." + ext
            else:
                base, ext = filename, ""

            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")

            key = f"raw/{user_id}/{exercise_type}/{new_filename}"

            url = s3.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": BUCKET, "Key": key},
                ExpiresIn=3600,
            )

            return {"statusCode": 200, "body": json.dumps({"url": url, "key": key})}

        elif method == "GET" and path == "/get-result":
            user_id = params.get("user_id")
            exercise_type = params.get("exercise_type")
            filename = params.get("filename")

            if not user_id or not exercise_type or not filename:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {"error": "user_id, exercise_type and filename are required"}
                    ),
                }

            key = f"processed/{user_id}/{exercise_type}/{filename}.zip"

            table = dynamodb.Table(DYNAMODB_TABLE)

            response = table.get_item(
                Key={"pk": f"video#{key}", "sk": f"user#{user_id}"}
            )

            if "Item" not in response:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Video not found"}),
                }

            if response["Item"]["status"] == "processing":
                return {
                    "statusCode": 200,
                    "body": json.dumps({"status": "processing"}),
                }

            if response["Item"]["status"] == "done":
                os.makedirs("/tmp", exist_ok=True)
                s3.download_file(
                    BUCKET,
                    response["Item"]["result_key"],
                    f"/tmp/{response['Item']['result_key']}",
                )

                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        {
                            "status": "done",
                            "result_key": response["Item"]["result_key"],
                            "result_url": response["Item"]["result_url"],
                        }
                    ),
                }

        else:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Not found"}),
            }

    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }


def get_upload_url(event: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a pre-signed URL for video upload"""
    # TODO: Implement pre-signed URL generation
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"upload_url": "placeholder"}),
    }


def get_video_status(event: Dict[str, Any]) -> Dict[str, Any]:
    """Check the processing status of a video"""
    # TODO: Query DynamoDB for video status
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"status": "processing"}),
    }


def get_video_results(event: Dict[str, Any]) -> Dict[str, Any]:
    """Get the analysis results for a processed video"""
    # TODO: Retrieve results from DynamoDB/S3
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"results": "placeholder"}),
    }
