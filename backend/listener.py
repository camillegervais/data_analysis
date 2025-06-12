from pyaccsharedmemory import accSharedMemory
import os
import django
# import pyvjoy

import time
import serial
import h5py  # Ajout de la bibliothèque pour gérer les fichiers HDF5
import numpy as np  # Ajout de NumPy pour gérer les tableaux

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import the models
from simracing.models import Compound, Track, Car, Driver, Session, Lap
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import datetime

from simracing.data_formating import lapFormating

def average(list):
    return sum(list)/len(list)


asm = accSharedMemory()

sm = asm.read_shared_memory()

print("Wait for shared memory")

while sm is None:
    sm = asm.read_shared_memory()

print("Shared memory found")

current_lap = sm.Graphics.completed_lap

# channel_layer = get_channel_layer()

sectors = []

current_sector = sm.Graphics.current_sector_index
current_start_distance = 0
current_start_time = 0

current_tyre_set = 1
number_lap_tyre = 0

current_h5_file = None  # Variable pour suivre le fichier HDF5 en cours
current_h5_filepath = None

# Initialisation des tableaux pour accumuler les données
telemetry_data = {
    "tyre_pressure": [],
    "tyre_temperature": [],
    "fuel": [],
    "air_temp": [],
    "speed": [],
    "gear": [],
    "g_force": [],
    "brake": [],
    "throttle": [],
    "brake_balance": [],
    "rpm": [],
    "wheel_speed": [],
    "wheel_slip": [],
    "brake_temp": [],
    "time": [],
    "distance": [],
    "yaw_angle": [],
    "steering_angle": [],
    "suspension_travel": [],
}

while True:
    sm = asm.read_shared_memory()
    if sm is not None:
        #append sector times during the lap
        if sm.Graphics.current_sector_index != current_sector:
            current_sector = sm.Graphics.current_sector_index
            sectors.append(sm.Graphics.current_time)

        #handle the change of tyres and the number of laps on a tyre set
        if sm.Graphics.current_tyre_set == current_tyre_set:
            number_lap_tyre += 1
        else:
            current_tyre_set = sm.Graphics.current_tyre_set
            number_lap_tyre = 1

        # Créer un nouveau fichier HDF5 au début d'un nouveau tour
        if current_lap != sm.Graphics.completed_lap:

            current_lap = sm.Graphics.completed_lap
            current_sector = sm.Graphics.current_sector_index
            current_start_distance = sm.Graphics.distance_traveled
            current_start_time = sm.Graphics.current_time

            h5_filename = f"lap_{current_lap}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.h5"
            current_h5_filepath = os.path.join("telemetry_data", h5_filename)
            os.makedirs("telemetry_data", exist_ok=True)
            current_h5_file = h5py.File(current_h5_filepath, "w")
            
            if current_h5_file:
                # Pousser les données accumulées dans le fichier HDF5
                for key, data in telemetry_data.items():
                    current_h5_file.create_dataset(key, data=np.array(data))
                current_h5_file.close()  # Fermer le fichier précédent

            # Réinitialiser les tableaux pour le nouveau tour
            telemetry_data = {key: [] for key in telemetry_data}

            print(f"Sectors: {sectors}")

            # Mise en forme des temps de secteur
            sectors = [
                sectors[0],
                sectors[1] - sectors[0],
                sm.Graphics.last_time - sectors[1]
            ]

            # Ajouter le chemin du fichier HDF5 à l'objet Lap
            info_lap = {
                'session': Session.objects.all().order_by('id').last(),
                'time': sm.Graphics.last_time,
                'compound': Compound.objects.get(name='dry_compound'),
                'date': datetime.date.today(),
                'temperature': sm.Physics.air_temp,
                'fuel': sm.Physics.fuel,
                'tyre_pressure_fr': sm.Physics.wheel_pressure.front_right,
                'tyre_pressure_fl': sm.Physics.wheel_pressure.front_left,
                'tyre_pressure_rr': sm.Physics.wheel_pressure.rear_right,
                'tyre_pressure_rl': sm.Physics.wheel_pressure.rear_left,
                'tyre_temperature_fr': sm.Physics.tyre_core_temp.front_right,
                'tyre_temperature_fl': sm.Physics.tyre_core_temp.front_left,
                'tyre_temperature_rr': sm.Physics.tyre_core_temp.rear_right,
                'tyre_temperature_rl': sm.Physics.tyre_core_temp.rear_left,
                'usure_plaquette': (sm.Physics.pad_life.front_left + sm.Physics.pad_life.front_right + sm.Physics.pad_life.rear_left + sm.Physics.pad_life.rear_right)/4,
                'lap_type': 'Completed',
                'lap_index_session': sm.Graphics.completed_lap,
                'lap_index_tyre': current_tyre_set,
                'sector1': sectors[0],
                'sector2': sectors[1],
                'sector3': sectors[2],
                'tc_level': sm.Graphics.tc_level,
                'abs_level': sm.Graphics.abs_level,
                'valid_lap': sm.Graphics.is_valid_lap,
                'tyre_set': current_tyre_set,
                'telemetry_file': current_h5_filepath  # Nouveau champ pour le fichier HDF5
            }
            Lap.objects.create(**info_lap)

            sectors = []  # Réinitialiser les secteurs pour le nouveau tour

            # #send data to channel for follow session
            # async_to_sync(channel_layer.group_send)(
            #     "follow-session",
            #     {
            #         "type": "add.lap",
            #         "id": Lap.objects.filter(session=Session.objects.all().order_by('id').last()).count()+1,
            #         "time": sm.Graphics.last_time,
            #         "temp": sm.Physics.air_temp,
            #         "fuel": sm.Physics.fuel,
            #         "compound": "dry_compound",
            #         "session_id": Session.objects.all().order_by('id').last().id,
            #         "lap_number": sm.Graphics.completed_lap,
            #         "track": Lap.objects.all().order_by('id').last().session.track.name,
            #         "driver": Lap.objects.all().order_by('id').last().session.driver.name,
            #     },
            # )
            # print('Lap pushed')

        # Ajouter les données de télémétrie dans les tableaux NumPy
        telemetry_data["tyre_pressure"].append([
            sm.Physics.wheel_pressure.front_left,
            sm.Physics.wheel_pressure.front_right,
            sm.Physics.wheel_pressure.rear_left,
            sm.Physics.wheel_pressure.rear_right
        ])
        telemetry_data["tyre_temperature"].append([
            sm.Physics.tyre_core_temp.front_left,
            sm.Physics.tyre_core_temp.front_right,
            sm.Physics.tyre_core_temp.rear_left,
            sm.Physics.tyre_core_temp.rear_right
        ])
        telemetry_data["fuel"].append(sm.Physics.fuel)
        telemetry_data["air_temp"].append(sm.Physics.air_temp)
        telemetry_data["speed"].append(sm.Physics.speed_kmh)
        telemetry_data["gear"].append(sm.Physics.gear)
        telemetry_data["g_force"].append([
            sm.Physics.g_force.x,
            sm.Physics.g_force.y,
            sm.Physics.g_force.z
        ])
        telemetry_data["brake"].append(sm.Physics.brake)
        telemetry_data["throttle"].append(sm.Physics.gas)
        telemetry_data["brake_balance"].append(sm.Physics.brake_bias)
        telemetry_data["rpm"].append(sm.Physics.rpm)
        telemetry_data["wheel_speed"].append([
            sm.Physics.wheel_angular_s.front_left,
            sm.Physics.wheel_angular_s.front_right,
            sm.Physics.wheel_angular_s.rear_left,
            sm.Physics.wheel_angular_s.rear_right
        ])
        telemetry_data["wheel_slip"].append([
            sm.Physics.wheel_slip.front_left,
            sm.Physics.wheel_slip.front_right,
            sm.Physics.wheel_slip.rear_left,
            sm.Physics.wheel_slip.rear_right
        ])
        telemetry_data["brake_temp"].append([
            sm.Physics.brake_temp.front_left,
            sm.Physics.brake_temp.front_right,
            sm.Physics.brake_temp.rear_left,
            sm.Physics.brake_temp.rear_right
        ])
        telemetry_data["time"].append(sm.Graphics.current_time - current_start_time)
        telemetry_data["distance"].append(sm.Graphics.distance_traveled - current_start_distance)
        telemetry_data["yaw_angle"].append(sm.Physics.heading)
        telemetry_data["steering_angle"].append(sm.Physics.steer_angle)
        telemetry_data["suspension_travel"].append([
            sm.Physics.suspension_travel.front_left,
            sm.Physics.suspension_travel.front_right,
            sm.Physics.suspension_travel.rear_left,
            sm.Physics.suspension_travel.rear_right
        ])

    time.sleep(0.02)



