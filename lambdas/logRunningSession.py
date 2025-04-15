import json
import boto3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('running_sessions')

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*", 
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    try:
        # Handle preflight request
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CORS preflight successful"})
            }

        body = json.loads(event["body"]) if "body" in event else event

        # Validate required fields
        required_fields = ['user_id', 'distance_km', 'duration_min']
        if not all(field in body for field in required_fields):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Missing required fields"})
            }

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Convert distance_km and duration_min to Decimal
        distance_km = Decimal(str(body['distance_km']))
        duration_min = Decimal(str(body['duration_min']))

        # Calculate average pace (minutes per km)
        avg_pace = round(duration_min / distance_km, 2)

        # Estimate calories burned
        calories_burned = round(distance_km * 60)

        # Calculate expiration time (30 days from now)
        expiration_time = int((datetime.utcnow() + timedelta(days=30)).timestamp())

        # Construct item
        item = {
            "user_id": body['user_id'],
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "distance_km": distance_km,
            "duration_min": duration_min,
            "avg_pace_min_km": avg_pace,
            "calories_burned": calories_burned,
            "expiration_time": expiration_time  # TTL attribute
        }

        # Write to DynamoDB
        table.put_item(Item=item)

        return {
            "statusCode": 201,
            "headers": headers,
            "body": json.dumps({"message": "Run logged successfully", "session_id": session_id})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
