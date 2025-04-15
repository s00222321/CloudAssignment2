import json
import boto3

# S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Hardcode the S3 bucket name here
    bucket_name = 'meals-archives'  # Replace with your actual S3 bucket name

    for record in event['Records']:
        if record['eventName'] == 'REMOVE':  # TTL deletions show up as REMOVE
            old_image = record['dynamodb'].get('OldImage', {})
            # Convert DynamoDB JSON to standard JSON
            item = {k: list(v.values())[0] for k, v in old_image.items()}
            
            # Construct the S3 object key (e.g., user_id/session_id.json)
            key = f"{item['user_id']}/{item['meal_id']}.json"
            
            try:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=json.dumps(item),
                    ContentType='application/json',
                    StorageClass='STANDARD_IA'  # Set the storage class to Infrequent Access
                )
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": f"Failed to store item in S3: {str(e)}"})
                }

    return {"statusCode": 200}
