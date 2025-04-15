import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('meals')

def lambda_handler(event, context):
    user_id = event.get('user_id')
    if not user_id:
        raise ValueError("Missing user_id in input")

    # 7-day window
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    # Query all meals for the user
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    meals = response.get('Items', [])
    
    # Filter meals from last 7 days
    weekly_meals = []
    for meal in meals:
        try:
            meal_time = datetime.fromisoformat(meal['timestamp'])
            if start_time <= meal_time <= end_time:
                weekly_meals.append(meal)
        except Exception as e:
            print(f"Skipping meal due to timestamp error: {e}")

    # Aggregate nutrition info
    total_calories = sum(float(m.get('calories', 0)) for m in weekly_meals)
    total_protein = sum(float(m.get('protein', 0)) for m in weekly_meals)
    total_carbs = sum(float(m.get('carbs', 0)) for m in weekly_meals)
    total_fat = sum(float(m.get('fat', 0)) for m in weekly_meals)

    return {
        'user_id': user_id,
        'week_start': start_time.strftime('%Y-%m-%d'),
        'week_end': end_time.strftime('%Y-%m-%d'),
        'total_calories': round(total_calories, 2),
        'total_protein_g': round(total_protein, 2),
        'total_carbs_g': round(total_carbs, 2),
        'total_fat_g': round(total_fat, 2),
        'meal_count': len(weekly_meals)
    }
