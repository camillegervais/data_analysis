import json
from channels.generic.websocket import WebsocketConsumer
import time
from asgiref.sync import async_to_sync

from .models import Lap, Session
from django.db.models import Avg, StdDev, Sum

from channels.layers import get_channel_layer


#consumer for the following of a session
class SimRacingConsumer(WebsocketConsumer):

    #method when a client connect to the server
    def connect(self):
        print('in connect function')
        self.accept()

        self.send(json.dumps({
            "type": "connected",
            "message": "You are connected, message from a send"
        }))
        #add the client to the group with the external program
        async_to_sync(self.channel_layer.group_add)("follow-session", self.channel_name)
        #send a message to the client when connected
        async_to_sync(self.channel_layer.group_send)(
            "follow-session",
            {
                "type": "connected",
                "message": "You follow a session.",
            },
        )
        print('server connected and message sent')

    def disconnect(self, close_code):
        #remove the client from the group with the external program
        async_to_sync(self.channel_layer.group_discard)("follow-session", self.channel_name)
        print('Disconnect')
        pass

    #handler for the connexion message sent by the server, and send this to everybody
    def connected(self, event):
        print('In connected function')

    #handler for the message when a lap is added, it is triggered when the message is sent by the external program and send back the information to everybody and especially to the client
    def add_lap(self, event):
        print('In add_lap function')
        message = json.dumps({
            "type": "add_lap_final",
            "id": event["id"],
            "time": event["time"],
            "track": event["track"], 
            "temp": event["temp"],
            "fuel": event["fuel"],
            "compound": event["compound"],
            "driver": event["driver"],
            "session_id": event["session_id"],
            "lap_number": event["lap_number"],
        })
        self.send(text_data=message)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "follow-session",
            {
                "type": "get.info",
                "session_id": event["session_id"]
            },
        )


    def get_info(self, event):
        print('In get_info function')
        id = event["session_id"]
        laps = Lap.objects.filter(session=Session.objects.get(id=id))
        message = json.dumps({
            "type": "get_info_final",
            "meanTime": laps.aggregate(Avg('time'))['time__avg'],
            "stdTime": laps.aggregate(StdDev('time'))['time__stddev'],
            "totalTime": laps.aggregate(Sum('time'))['time__sum'],
            "tyre_pressure": {
                "fr": laps.order_by('id').last().tyre_pressure_fr,
                "fl": laps.order_by('id').last().tyre_pressure_fl,
                "rr": laps.order_by('id').last().tyre_pressure_rr,
                "rl": laps.order_by('id').last().tyre_pressure_rl,
            },
            "tyre_temp": {
                "fr": laps.order_by('id').last().tyre_temperature_fr,
                "fl": laps.order_by('id').last().tyre_temperature_fl,
                "rr": laps.order_by('id').last().tyre_temperature_rr,
                "rl": laps.order_by('id').last().tyre_temperature_rl,
            },
            "fuel": laps.order_by('id').last().fuel,
            "brake_pad": laps.order_by('id').last().usure_plaquette
        })
        self.send(text_data=message)
    
    