import json
import uuid
import hashlib
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST"
    }

    try:
        body = json.loads(event['body'])
        username = body['username']
        email = body['email']
        password = body['password']

        user_id = str(uuid.uuid4())
        hashed_pw = hash_password(password)

        # Save user to DynamoDB
        table.put_item(Item={
            'user_id': user_id,
            'username': username,
            'email': email,
            'password': hashed_pw
        })

        return {
            "statusCode": 201,
            "headers": headers,
            "body": json.dumps({
                "message": "User created successfully",
                "user_id": user_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": str(e)
            })
        }
