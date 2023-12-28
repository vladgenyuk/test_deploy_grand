import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Messages


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.receiver_group_name = 'chat_%s' % self.chat_id
        print(self.scope)

        async_to_sync(self.channel_layer.group_add)(
            self.receiver_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.receiver_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = str(self.scope['user'])

        async_to_sync(self.channel_layer.group_send)(
            self.receiver_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )
        if message:
            Messages.objects.create(
                author=self.scope['user'],
                text=message,
                chat_id=int(self.scope['url_route']['kwargs']['chat_id'])
            )

    def chat_message(self, event):
        message = event['message']
        username = event['username']

        self.send(text_data=json.dumps({
            'event': "Send",
            'message': message,
            'username': username
        }))
