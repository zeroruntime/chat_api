import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle user connection to WebSocket."""
        self.user = self.scope['user']
        
        # Ensure the user is authenticated
        if self.user.is_authenticated:
            # Set user online when connecting
            self.user.set_online()
            
            # Send a welcome message (optional)
            await self.send(text_data=json.dumps({
                'message': f'Welcome, {self.user.username}!',
            }))
            
            # Accept the WebSocket connection
            await self.accept()

    async def disconnect(self, close_code):
        """Handle user disconnecting from WebSocket."""
        if self.user.is_authenticated:
            # Set user offline when disconnecting
            self.user.set_offline()
            
            # Update the last_seen timestamp to the current time on disconnect
            self.user.update_last_seen()  # Set the `last_seen` to now

        # Optionally, broadcast to other users that the user has disconnected
        await self.send(text_data=json.dumps({
            'message': f'{self.user.username} has disconnected.',
        }))

    async def receive(self, text_data):
        """Handle incoming messages."""
        if self.user.is_authenticated:
            # Process the message and broadcast it to other users
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            # Update `last_seen` timestamp when the user sends a message
            self.user.update_last_seen()

            # Example: Send a message to all connected clients (broadcast)
            await self.send(text_data=json.dumps({
                'message': f'{self.user.username}: {message}',
            }))

    async def send_to_group(self, message):
        """Send a message to a group of users."""
        await self.send(text_data=json.dumps({
            'message': message,
        }))
