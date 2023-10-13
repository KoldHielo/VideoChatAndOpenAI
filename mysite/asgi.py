"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
import main.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

django_app = get_asgi_application()

application = ProtocolTypeRouter({
  'http': django_app,
  'https': django_app,
  'websocket': AllowedHostsOriginValidator(
    AuthMiddlewareStack(
      URLRouter(
        main.routing.websocket_urlpatterns
      )
    )
  )
})
