import json
import boto3

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('running_sessions')

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,DELETE"
    }

    try:
        # Handle preflight request
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CORS preflight successful"})
            }

        # Extract user_id and session_id from path parameters
        path_params = event.get("pathParameters", {})
        user_id = path_params.get("user_id")
        session_id = path_params.get("session_id")

        if not user_id or not session_id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Both user_id and session_id are required"})
            }

        # Delete the item from DynamoDB using the composite key
        response = table.delete_item(
            Key={
                'user_id': user_id,
                'session_id': session_id
            }
        )

        # Check if the delete was acknowledged
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "Session deleted successfully"})
            }
        else:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"error": "Session not found"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
