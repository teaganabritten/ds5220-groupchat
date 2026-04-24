import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('chat-connections')

def handler(event, context):
    connection_id = event['requestContext']['connectionId']
    
    table.delete_item(Key={'connectionId': connection_id})
    
    return {'statusCode': 200}
