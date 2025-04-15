import boto3
import json

# AWS clients
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/370706567264/UserIDQueue'

def get_user_ids():
    table = dynamodb.Table('users')
    response = table.scan() 
    user_ids = [item['user_id'] for item in response['Items']]
    return user_ids

def enqueue_user_ids(user_ids):
    for user_id in user_ids:
        message = {
            'user_id': user_id
        }
        sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

def lambda_handler(event, context):
    # Fetch all user IDs from DynamoDB
    user_ids = get_user_ids()
    
    # Enqueue the user IDs into the SQS queue
    enqueue_user_ids(user_ids)
    
    return {
        'statusCode': 200,
        'body': 'User IDs enqueued successfully.'
    }
