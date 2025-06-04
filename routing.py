from django.urls import re_path
from app.consumers import ResourceNotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", ResourceNotificationConsumer.as_asgi()),
]
