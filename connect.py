import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('chat-connections')

def handler(event, context):
    connection_id = event['requestContext']['connectionId']
    ttl = int(time.time()) + 7200  # 2 hours
    
    table.put_item(Item={
        'connectionId': connection_id,
        'ttl': ttl
    })
    
    return {'statusCode': 200}
