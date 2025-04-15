import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('meals')

def lambda_handler(event, context):
    try:
        # Check HTTP method (DELETE)
        if event['httpMethod'] == 'DELETE':
            # Extract path parameters from the event
            user_id = event['pathParameters']['user_id']
            meal_id = event['pathParameters']['meal_id']

            # Delete the item from the DynamoDB table
            response = table.delete_item(
                Key={
                    'user_id': user_id,
                    'meal_id': meal_id
                }
            )

            # Check if the item was found and deleted
            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                    },
                    'body': json.dumps({
                        'message': 'Meal entry deleted successfully',
                        'user_id': user_id,
                        'meal_id': meal_id
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                    },
                    'body': json.dumps({
                        'message': 'Meal entry not found',
                        'user_id': user_id,
                        'meal_id': meal_id
                    })
                }

        # If not DELETE method, return method not allowed
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
                },
                'body': json.dumps({
                    'message': 'Method not allowed'
                })
            }

    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'
            },
            'body': json.dumps({
                'message': 'Failed to delete meal entry',
                'error': str(e)
            })
        }
