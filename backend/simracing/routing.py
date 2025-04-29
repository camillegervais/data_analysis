from django.urls import re_path

from . import consumers

#redirect to the consumer for the follow-session
websocket_urlpatterns = [
    re_path(
        r"ws/simracing/",
        consumers.SimRacingConsumer.as_asgi(),
    ),
]