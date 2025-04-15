import boto3
import json
from datetime import datetime
import os

s3 = boto3.client('s3')
bucket_name = 'weekly-fitness-reports'

def lambda_handler(event, context):
    running_data = event.get('running_data')
    meal_data = event.get('meal_data')

    if not running_data or not meal_data:
        raise ValueError("Missing running_data or meal_data")

    user_id = running_data['user_id']
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')
    report_key = f'reports/{user_id}/progress_report_{timestamp}.json'

    # Construct report structure
    report = {
        "user_id": user_id,
        "generated_at": timestamp,
        "week_range": {
            "start": running_data.get("week_start"),
            "end": running_data.get("week_end")
        },
        "running_summary": {
            "total_distance_km": running_data["total_distance_km"],
            "total_duration_min": running_data["total_duration_min"],
            "total_calories_burned": running_data["total_calories_burned"],
            "avg_pace_min_km": running_data["avg_pace_min_km"],
            "sessions": running_data["session_count"]
        },
        "nutrition_summary": {
            "total_calories": meal_data["total_calories"],
            "total_protein_g": meal_data["total_protein_g"],
            "total_carbs_g": meal_data["total_carbs_g"],
            "total_fat_g": meal_data["total_fat_g"],
            "meals": meal_data["meal_count"]
        }
    }

    # Upload to S3
    s3.put_object(
        Bucket=bucket_name,
        Key=report_key,
        Body=json.dumps(report, indent=2),
        ContentType='application/json'
    )

    return {
        "status": "success",
        "report_key": report_key,
        "s3_url": f"s3://{bucket_name}/{report_key}",
        "user_id": user_id
    }
