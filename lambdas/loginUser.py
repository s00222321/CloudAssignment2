import json
import hashlib
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        }

        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        username = body['username']
        password = body['password']
        hashed_pw = hash_password(password)

        # Query using the GSI
        response = table.query(
            IndexName='username-index',  # use the exact name of your GSI
            KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(username)
        )

        if not response['Items']:
            return {
                "statusCode": 401,
                "headers": headers,
                "body": json.dumps({"error": "User not found"})
            }

        user = response['Items'][0]

        if user['password'] != hashed_pw:
            return {
                "statusCode": 401,
                "headers": headers,
                "body": json.dumps({"error": "Invalid password"})
            }

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "message": "Login successful",
                "user_id": user['user_id'],
                "username": user['username']
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
