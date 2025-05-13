import os
import django
import numpy as np
import h5py
import matplotlib.pyplot as plt

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
    plt.title(f"Speed of lap {lap.id}")
    plt.xlabel('Distance (m)')
    plt.ylabel('Speed (m/s)')
    plt.grid()
    plt.show()

def explore_database(object_name):
    '''
    Explore the database and print the fields of the object.
    '''
    if object_name.lower() == 'lap':
        laps = Lap.objects.all()
        print("Lap fields:")
        for lap in laps:
            for field in lap._meta.get_fields():
                print(field.name)
    elif object_name.lower() == 'track':
        tracks = Track.objects.all()
        print("Track fields:")
        for track in tracks:
            for field in track._meta.get_fields():
                print(field.name)
    elif object_name.lower() == 'car':
        cars = Car.objects.all()
        print("Car fields:")
        for car in cars:
            for field in car._meta.get_fields():
                print(field.name)
    elif object_name.lower() == 'session':
        sessions = Session.objects.all()
        print("Session fields:")
        for session in sessions:
            for field in session._meta.get_fields():
                print(field.name)
    else:
        print("Object not found")
