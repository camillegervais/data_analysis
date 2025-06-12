import os
import django
import numpy as np
import json
from scripts_analysis.utils import format_lap_time, format_temperature

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track, Car, Session
from simracing.data_formating import lapFormating

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
            print(f'Sector 1: {format_lap_time(lap.sector1)}')
            print(f'Sector 2: {format_lap_time(lap.sector2)}')
            print(f'Sector 3: {format_lap_time(lap.sector3)}')
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

def exportJsonLap(lap):
    """
    Function to export a lap in JSON format.
    """
    lap_data = lapFormating(lap)
    lap_data['date'] = lap.date.strftime('%Y-%m-%d %H:%M:%S') if lap.date else None
    lap_data['csv_file'] = lap.telemetry_file.path.replace('.h5', '.csv') if lap.telemetry_file else None
    json_path = lap_data['csv_file'].replace('.csv', '.json')
    with open(json_path, 'w') as f:
        json.dump(lap_data, f)
    return json_path

def exportCSVLap(lap):
    """
    Function to export the data of a lap stored in a h5 file in a CSV format.
    """
    import h5py
    import pandas as pd

    lap = Lap.objects.get(id=lap.id)
    h5_file = h5py.File(lap.telemetry_file.path, 'r')

    data = {}

    # Extract data from the h5 file
    for key in h5_file.keys():
        if len(h5_file[key].shape) > 1:
            for i in range(h5_file[key].shape[1]):
                data[f'{key}_{i}'] = h5_file[key][:, i]
        else:
            data[key] = h5_file[key][:]

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Export to CSV
    csv_path = lap.telemetry_file.path.replace('.h5', '.csv')
    df.to_csv(csv_path, index=False)

    h5_file.close()
    return csv_path

def export_lap_data(lap):
    """
    Function to export lap data in both JSON and CSV formats.
    """
    json_path = exportJsonLap(lap)
    csv_path = exportCSVLap(lap)
    return json_path, csv_path