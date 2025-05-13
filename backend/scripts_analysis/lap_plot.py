import os
import django
import numpy as np
import h5py
import matplotlib.pyplot as plt
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track, Session, Car

def traction_circle(lap_id):
    '''
    Plot the traction circle of the lap.
    '''

    lap = Lap.objects.get(id=lap_id)

    with h5py.File(lap.telemetry_file.path, 'r') as f:
        g_lat = f['g_force'][:, 0]
        g_long = f['g_force'][:, 1]

        plt.scatter(g_lat, g_long)
        plt.axhline(0, color='black', lw=1)
        plt.axvline(0, color='black', lw=1)
        plt.grid()
        plt.show()

def speed_plot(lap_id):
    '''
    Plot the speed of the lap.
    '''

    for id in lap_id:
        lap = Lap.objects.get(id=int(id))

        with h5py.File(lap.telemetry_file.path, 'r') as f:
            speed = f['speed'][:]
            distance = f['distance'][:]

            if id == lap_id[0]:
                plt.plot(distance, speed, color='red')
            else:
                plt.plot(distance, speed, color='black')

    track = Track.objects.get(id=lap.session.track.id)
    for beacon in json.loads(track.lap_beacons).values():
        plt.axvline(x=beacon, color='blue', lw=1)
    plt.title(f"Speed of lap {lap.id}")
    plt.xlabel('Distance (m)')
    plt.ylabel('Speed (m/s)')
    plt.grid()
    plt.show()

def set_lap_beacons(track_id, beacons):
    '''
    Set the lap beacons for the lap and verify it is valid.
    The beacons list must be a dictionary with the following elements:
    - the key is the name of the sector
    - the value is the position of the start of the sector
    The value with the key start must be zero, so the key start mus be in the dictionary.
    '''

    track = Track.objects.get(id=track_id)
    if not isinstance(beacons, dict):
        print("Beacons must be a dictionary")
        return False
    if beacons.get('start') != 0:
        print("The first value must be zero")
        return False
    for beacon in beacons.values():
        if int(beacon) > track.length:
            print(f"Beacon {beacon} is out of track length {lap.session.track.length}")
            return False
        
    track.lap_beacons = json.dumps(beacons)
    track.save()