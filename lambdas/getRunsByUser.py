import boto3
import json
from decimal import Decimal

# Set up DynamoDB resource
current_region = "us-east-1"
dynamodb = boto3.resource('dynamodb', region_name=current_region)
table = dynamodb.Table('running_sessions')

# Helper function to convert Decimal to float
def decimal_to_float(item):
    for key, value in item.items():
        if isinstance(value, Decimal):
            item[key] = float(value)
    return item

# Function to log messages based on log level
def log_message(level, message):
    if level == 'DEBUG':
        print(f"DEBUG: {message}")
    elif level == 'INFO':
        print(f"INFO: {message}")
    elif level == 'WARN':
        print(f"WARNING: {message}")
    elif level == 'ERROR':
        print(f"ERROR: {message}")

# Helper function to determine allowed CORS origin
def get_cors_origin(event):
    stage_vars = event.get("stageVariables", {})
    allowed_origins = stage_vars.get("allowedOrigins", "*")
    origin = event.get("headers", {}).get("origin", "")
    print(f"Allowed Origins: {allowed_origins}, Request Origin: {origin}")

    if allowed_origins == "*":
        return "*"
    else:
        allowed_list = [o.strip() for o in allowed_origins.split(",")]
        return origin if origin in allowed_list else "null"

def lambda_handler(event, context):
    try:
        stage_vars = event.get("stageVariables", {})
        log_level = stage_vars.get("logLevel", "ERROR")
        print("Stage Variable log level:", log_level)

        cors_origin = get_cors_origin(event)

        # Extract user_id from the path parameters
        user_id = event.get('pathParameters', {}).get('user_id')
        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required user_id"}),
                "headers": {
                    "Access-Control-Allow-Origin": cors_origin,
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            }

        log_message(log_level, f"Querying runs for user_id: {user_id}")

        # Query DynamoDB
        response = table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id}
        )

        if 'Items' in response and response['Items']:
            converted_items = [decimal_to_float(item) for item in response['Items']]
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Runs retrieved successfully",
                    "data": converted_items
                }),
                "headers": {
                    "Access-Control-Allow-Origin": cors_origin,
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No runs found for this user"}),
                "headers": {
                    "Access-Control-Allow-Origin": cors_origin,
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": get_cors_origin(event),
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }
