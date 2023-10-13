from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
  re_path('VideoChat/ws/VideoChat', consumers.VideoChatConsumer.as_asgi()),
]
