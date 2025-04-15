import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('running_sessions')

def lambda_handler(event, context):
    user_id = event.get('user_id')
    if not user_id:
        raise ValueError("Missing user_id in input")

    # Define the 7-day window
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    # Query all sessions for the user
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    sessions = response.get('Items', [])
    
    # Filter sessions from the last 7 days
    weekly_sessions = []
    for session in sessions:
        try:
            session_time = datetime.fromisoformat(session['timestamp'])
            if start_time <= session_time <= end_time:
                weekly_sessions.append(session)
        except Exception as e:
            print(f"Skipping session due to timestamp error: {e}")

    # Aggregate data
    total_distance = sum(float(s['distance_km']) for s in weekly_sessions)
    total_duration = sum(float(s['duration_min']) for s in weekly_sessions)
    total_calories = sum(float(s['calories_burned']) for s in weekly_sessions)

    # Calculate average pace
    avg_pace = (
        round(sum(float(s['avg_pace_min_km']) for s in weekly_sessions) / len(weekly_sessions), 2)
        if weekly_sessions else None
    )

    return {
        'user_id': user_id,
        'week_start': start_time.strftime('%Y-%m-%d'),
        'week_end': end_time.strftime('%Y-%m-%d'),
        'total_distance_km': round(total_distance, 2),
        'total_duration_min': round(total_duration, 2),
        'total_calories_burned': round(total_calories, 2),
        'avg_pace_min_km': avg_pace,
        'session_count': len(weekly_sessions)
    }
