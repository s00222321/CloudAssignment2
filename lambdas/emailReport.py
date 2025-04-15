import os
import boto3
import json
import urllib.parse

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

USERS_TABLE_NAME = "users"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:370706567264:sns-demo"

def render_text(data):
    # Extract the running and nutrition data from the input
    running_summary = data['running_summary']
    nutrition_summary = data['nutrition_summary']
    
    # Format the data into a plain text format
    return f"""
Weekly Progress Report

You've been doing amazing, keep up the good work!

Running Summary:
Total Distance: {running_summary['total_distance_km']} km
Total Duration: {running_summary['total_duration_min']} min
Total Calories Burned: {running_summary['total_calories_burned']}
Average Pace: {running_summary['avg_pace_min_km']} min/km
Sessions: {running_summary['sessions']}

Nutrition Summary:
Total Calories: {nutrition_summary['total_calories']}
Protein: {nutrition_summary['total_protein_g']}g | Carbs: {nutrition_summary['total_carbs_g']}g | Fat: {nutrition_summary['total_fat_g']}g
Meals: {nutrition_summary['meals']}
"""

def get_user_email(user_id):
    table = dynamodb.Table(USERS_TABLE_NAME)
    response = table.get_item(Key={"user_id": user_id})
    return response['Item']['email']

def subscribe_email_if_not_already(topic_arn, email):
    response = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
    for sub in response['Subscriptions']:
        if sub['Endpoint'] == email and sub['Protocol'] == 'email':
            print("Email already subscribed.")
            return

    sub_response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )
    print("Subscription initiated. Check inbox to confirm.")
    print("Subscription ARN:", sub_response['SubscriptionArn'])

def lambda_handler(event, context):
    # Directly extract input from the event
    s3_url = event["report_data"]["s3_url"]
    user_id = event["user_id"]

    # Parse the S3 URL to get the bucket and key
    parsed = urllib.parse.urlparse(s3_url)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')

    # Retrieve the progress report from S3
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    report_json = json.loads(obj['Body'].read())

    # Get user email using the user_id
    user_email = get_user_email(user_id)

    # Create the text content for the email
    text_content = render_text(report_json)

    # Ensure email is subscribed to the SNS topic
    subscribe_email_if_not_already(SNS_TOPIC_ARN, user_email)

    # Publish the message to the SNS topic
    response = sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=text_content,
        Subject="Your Weekly Progress Report"
    )

    return {
        "statusCode": 200,
        "body": f"SNS message sent to topic. Message ID: {response['MessageId']}, to {user_email}"
    }
