import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('chat-connections')

def handler(event, context):
    request_context = event['requestContext']
    domain = request_context['domainName']
    stage = request_context['stage']
    
    body = json.loads(event['body'])
    username = body.get('username', 'anon')
    message = body.get('message', '')
    
    # Build Management API endpoint
    endpoint = f'https://{domain}/{stage}'
    apigw = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=endpoint
    )
    
    # Get all connections
    response = table.scan()
    connections = response.get('Items', [])
    
    payload = json.dumps({'username': username, 'message': message}).encode()
    
    for conn in connections:
        connection_id = conn['connectionId']
        try:
            apigw.post_to_connection(
                ConnectionId=connection_id,
                Data=payload
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'GoneException':
                # Client disconnected ungracefully — clean up
                table.delete_item(Key={'connectionId': connection_id})
            else:
                raise
    
    return {'statusCode': 200}
