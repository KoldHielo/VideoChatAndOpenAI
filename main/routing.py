from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
  re_path('ws/VideoChat', consumers.VideoChatConsumer.as_asgi()),
]
