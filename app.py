import json
import time
import boto3
from botocore.exceptions import ClientError
from chalice import Chalice

app = Chalice(app_name='chat-app')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('chat-connections')


@app.on_ws_connect()
def connect(event):
    table.put_item(Item={
        'connectionId': event.connection_id,
        'ttl': int(time.time()) + 7200
    })


@app.on_ws_disconnect()
def disconnect(event):
    table.delete_item(Key={'connectionId': event.connection_id})


@app.on_ws_message()
def message(event):
    body = json.loads(event.body)
    username = body.get('username', 'anon')
    msg = body.get('message', '')

    apigw = app.websocket_api.session.client(
        'apigatewaymanagementapi',
        endpoint_url=event.domain_name + '/' + event.stage
    )

    response = table.scan()
    connections = response.get('Items', [])

    payload = json.dumps({'username': username, 'message': msg}).encode()

    for conn in connections:
        cid = conn['connectionId']
        try:
            apigw.post_to_connection(ConnectionId=cid, Data=payload)
        except ClientError as e:
            if e.response['Error']['Code'] == 'GoneException':
                table.delete_item(Key={'connectionId': cid})
            else:
                raise
