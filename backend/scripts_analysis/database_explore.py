import os
import django
import numpy as np
from scripts_analysis.utils import format_lap_time, format_temperature

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track, Car, Session

def explore_database(object_name):
    '''
    Function to explore the database and get the data of the object.
    Require the object name in the database.
    '''
    print('-------------------')
    if object_name.lower() == 'lap':
        laps = Lap.objects.all()
        for lap in laps:
            print(f'Lap ID: {lap.id}, Track: {lap.session.track.name}, Driver: {lap.session.driver.name}')
            print(f'Lap Time: {format_lap_time(lap.time)}')
            print(f'Telemetry file: {lap.telemetry_file.path}')
            print(f'Compound: {lap.compound.name}')
            print(f'Fuel: {lap.fuel}')
            print(f'Temperature: {format_temperature(lap.temperature)}')
            print('-------------------')
    elif object_name.lower() == 'track':
        tracks = Track.objects.all()
        for track in tracks:
            print(f'Track ID: {track.id}, Name: {track.name}')
            print(f'Length: {track.length}, Country: {track.country}')
            print(f'Turns count: {track.turn}')
            print('-------------------')
    elif object_name.lower() == 'car':
        cars = Car.objects.all()
        for car in cars:
            print(f'Car ID: {car.id}, Name: {car.name}')
            print(f'Manufacturer: {car.manufacturer}, Model: {car.model}')
            print(f'Year: {car.year}, Weight: {car.weight}')
            print(f'Power: {car.power}, Torque: {car.torque}')
            print(f'Top Speed: {car.top_speed}')
            print('-------------------')
    elif object_name.lower() == 'session':
        sessions = Session.objects.all()
        for session in sessions:
            print(f'Session ID: {session.id}, Driver: {session.driver.name}')
            print(f'Track: {session.track.name}, Car: {session.car.name}')
            print(f'Date: {session.date}, Weather: {session.weather}')
            print(f'Session Type: {session.session_type}')
            print('-------------------')
    else:
        print('Object not found in the database')