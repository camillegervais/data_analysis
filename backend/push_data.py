import os
import django
import datetime

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import time
import random

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import the models
from simracing.models import Compound, Track, Car, Driver, Lap, Session

def populate_track():
    # Create and save instances
    id = Track.objects.count() + 1
    info_track = {'id': id, 'name': 'Misano', 'length': 4064, 'country': 'Italy', 'turn': 16}
    Track.objects.create(**info_track)

def populate_car():
    # Create and save instances
    id = Car.objects.count() + 1
    info_car = {'id': id, 'name': 'Ferrari 488 GT3 Evo', 'manufacturer': 'Ferrari', 'model': '488 GT3 Evo', 'year': 2020, 'weight': 1260, 'power': 600, 'torque': 700, 'top_speed': 285}
    Car.objects.create(**info_car)

#examples of functions to push data in the database and send info to the websocket
def populate_lap():
    for i in range(5):
        comp = Compound.objects.get(id = 1)
        tyre_pres = random.randint(260, 280)/10
        info_lap = {
                    'session': Session.objects.all().order_by('id').last(),
                    'time': random.randint(100000, 150000),
                    'compound': Compound.objects.get(name='dry_compound'),
                    'date': datetime.date.today(),
                    'temperature': 27,
                    'fuel': random.randint(0, 70),
                    'tyre_pressure_fr': tyre_pres,
                    'tyre_pressure_fl': tyre_pres,
                    'tyre_pressure_rr': tyre_pres,
                    'tyre_pressure_rl': tyre_pres,
                    'tyre_temperature_fr': 91,
                    'tyre_temperature_fl': 90,
                    'tyre_temperature_rr': 92,
                    'tyre_temperature_rl': 92,
                    'usure_plaquette': 28.8,
                    'lap_type': 'Completed',
                    'lap_index_session': i+1,
                }
        Lap.objects.create(**info_lap)
        sendLap(i, info_lap)

#send a serie of 5 laps to the follow session group
def sendLap(id, info):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "follow-session",
        {
            "type": "add.lap",
            "id": id,
            "time": info['time'],
            "track": info['session'].track.name, 
            "temp": info['temperature'],
            "fuel": info['fuel'],
            "compound": "dry_compound",
            "driver": info['session'].driver.name,
            "session_id": Session.objects.all().order_by('id').last().id,
            "lap_number": Lap.objects.filter(session=Session.objects.all().order_by('id').last()).count()+1
        },
    )
    time.sleep(2)

def deleteLap():
    Lap.objects.all().delete()

def deleteSession():
    Session.objects.all().delete()

if __name__ == '__main__':
    deleteLap()
    deleteSession()