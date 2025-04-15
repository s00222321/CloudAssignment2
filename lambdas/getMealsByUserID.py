import json
import boto3
from decimal import Decimal

# Initialize DynamoDB client
current_region = "us-east-1"
dynamodb = boto3.resource('dynamodb', region_name=current_region)
table = dynamodb.Table('meals')

def decimal_to_float(value):
    """Recursively converts Decimal types to float."""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, dict):
        return {key: decimal_to_float(val) for key, val in value.items()}
    elif isinstance(value, list):
        return [decimal_to_float(item) for item in value]
    else:
        return value

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
        # Check HTTP method (GET)
        if event['httpMethod'] == 'GET':
            # Extract user_id from path parameters
            user_id = event['pathParameters']['user_id']
            stage_vars = event.get("stageVariables", {})
            log_level = stage_vars.get("logLevel", "ERROR")
            print("Stage Variable log level:", log_level)
            cors_origin = get_cors_origin(event)

            log_message(log_level, f"Querying meals for user_id: {user_id}")

            # Query DynamoDB to get all meals for the user_id
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )

            # Check if there are any items in the response
            if 'Items' in response and len(response['Items']) > 0:
                # Convert Decimal types to float
                meals = decimal_to_float(response['Items'])

                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': cors_origin,
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                    },
                    'body': json.dumps({
                        'message': 'Meals retrieved successfully',
                        'user_id': user_id,
                        'meals': meals
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': cors_origin,
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                    },
                    'body': json.dumps({
                        'message': 'No meals found for the user',
                        'user_id': user_id
                    })
                }

        # If not GET method, return method not allowed
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': cors_origin,
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                },
                'body': json.dumps({
                    'message': 'Method not allowed'
                })
            }

    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': cors_origin,
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            },
            'body': json.dumps({
                'message': 'Failed to retrieve meals',
                'error': str(e)
            })
        }


