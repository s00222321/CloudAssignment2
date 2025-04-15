import json
import boto3
from uuid import uuid4
from datetime import datetime, timedelta

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('meals')

def lambda_handler(event, context):
    try:
        # Parse the incoming JSON payload
        body = json.loads(event['body'])

        # Extract data from the request body
        user_id = body['user_id']
        meal_type = body['meal_type']
        calories = body['calories']
        carbs = body['carbs']
        protein = body['protein']
        fat = body['fat']
        food_items = body.get('food_items', []) 

        # Generate a unique MealID (could be timestamp or UUID)
        meal_id = str(uuid4())  # UUID for uniqueness
        timestamp = datetime.utcnow().isoformat()  # ISO 8601 timestamp
        expiration_time = int((datetime.utcnow() + timedelta(days=30)).timestamp())

        # Construct the item to be added to DynamoDB
        item = {
            'user_id': user_id,
            'meal_id': meal_id,
            'meal_type': meal_type,
            'calories': calories,
            'carbs': carbs,
            'protein': protein,
            'fat': fat,
            'food_items': food_items,
            'timestamp': timestamp,
            "expiration_time": expiration_time
        }

        # Add the new entry to the DynamoDB table
        table.put_item(Item=item)

        # Return success response with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'message': 'Meal entry added successfully',
                'meal_id': meal_id
            })
        }

    except Exception as e:
        # Return error response with CORS headers
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'message': 'Failed to add meal entry',
                'error': str(e)
            })
        }
