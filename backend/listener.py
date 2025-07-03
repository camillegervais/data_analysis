from pyaccsharedmemory import accSharedMemory
import os
import django
import sys

import pyvjoy
import serial
import serial.tools.list_ports
import struct

import time
import h5py  # Ajout de la bibliothèque pour gérer les fichiers HDF5
import numpy as np  # Ajout de NumPy pour gérer les tableaux
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import the models
from simracing.models import Compound, Track, Car, Driver, Session, Lap
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import datetime

from simracing.data_formating import lapFormating

time.sleep(0.5)

redis = False
wheel = False
if '--redis' in sys.argv:
    redis = True
    print(Fore.BLUE + "Redis will be activated" + Style.RESET_ALL)
if '--wheel' in sys.argv:
    wheel = True
    print(Fore.BLUE + "Steering wheel will be used" + Style.RESET_ALL)


def average(list):
    return sum(list)/len(list)

print(Fore.RED + "Starting ACC Listener..." + Style.RESET_ALL)

print(Fore.BLUE + "Waiting for shared memory..." + Style.RESET_ALL)

if redis:
    channel_layer = get_channel_layer()
    print(Fore.GREEN + "Redis channel set up" + Style.RESET_ALL)

# Setup all the hardware for the communication with the steering wheel
if wheel:
    j = pyvjoy.VJoyDevice(1)
    # useful functions
    def average(list):
        return sum(list)/len(list)

    # on établit la communication série avec l'Arduino
    baud = 115200
    arduino = serial.Serial(port = "COM10", baudrate = baud, timeout=1)
    # Format string for struct packing
    # !: network byte order (big-endian)
    # B: unsigned char (1 byte) - for gear, flags, levels
    # f: float (4 bytes) - for pressures
    # l: long (4 bytes) - for time values in milliseconds
    # h: short (2 bytes) - for position, lap, speed
    DATA_FORMAT = "<BhBfffflBlBBllfBBfhh"

    # Function to calculate CRC-8
    def calculate_crc(data):
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    print(Fore.GREEN + "Steering wheel set up" + Style.RESET_ALL)

asm = accSharedMemory()

sm = asm.read_shared_memory()

while sm is None:
    sm = asm.read_shared_memory()

print(Fore.GREEN + "Shared memory found" + Style.RESET_ALL)

current_lap = sm.Graphics.completed_lap

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
    "speed": [],
    "gear": [],
    "g_force": [],
    "brake": [],
    "throttle": [],
    "brake_balance": [],
    "rpm": [],
    "wheel_speed": [],
    "slip_ratio": [],
    "slip_angle": [],
    "brake_temp": [],
    "time": [],
    "distance": [],
    "yaw_angle": [],
    "steering_angle": [],
    "suspension_travel": [],
}

while True:
    sm = asm.read_shared_memory()

    # logic for the steering wheel
    if wheel:
        # initialize variables
        rpm_percent = 0
        pad_wear = 0

        # if the Arduino is connected
        if arduino.isOpen():
            # send game data if it is running
            if sm is not None:
                # format data for the Arduino
                flags = ((int(sm.Physics.tc) & 1) << 4) | ((int(sm.Physics.abs) & 1) << 3) | (sm.Physics.pit_limiter_on << 2) | (sm.Graphics.is_valid_lap << 1) | sm.Graphics.is_delta_positive
                if not sm.Static.max_rpm == 0:
                    rpm_percent = int((sm.Physics.rpm/sm.Static.max_rpm)*100)
                pad_wear = round(average([sm.Physics.wheel_pressure.front_left, 
                                        sm.Physics.wheel_pressure.front_right, 
                                        sm.Physics.wheel_pressure.rear_left, 
                                        sm.Physics.wheel_pressure.rear_right]), 1)

                # Add input validation and type conversion before packing
                data = struct.pack(DATA_FORMAT,
                    int(sm.Physics.gear) & 0xFF,                    # 1 byte
                    int(sm.Physics.speed_kmh),                      # 2 bytes
                    int(flags),                                     # 1 byte flags
                    float(sm.Physics.wheel_pressure.front_left),    # 4 bytes
                    float(sm.Physics.wheel_pressure.front_right),   # 4 bytes
                    float(sm.Physics.wheel_pressure.rear_left),     # 4 bytes
                    float(sm.Physics.wheel_pressure.rear_right),    # 4 bytes
                    int(abs(sm.Graphics.delta_lap_time)),           # 4 bytes
                    rpm_percent & 0xFF,                             # 1 byte
                    int(sm.Graphics.best_time),                     # 4 bytes
                    int(sm.Physics.fuel) & 0xFF,                    # 1 byte
                    int(sm.Graphics.tc_level) & 0xFF,               # 1 byte
                    int(sm.Graphics.gap_ahead),                     # 4 bytes
                    int(sm.Graphics.last_time),                     # 4 bytes
                    float(pad_wear),                                # 4 bytes
                    int(sm.Graphics.abs_level) & 0xFF,              # 1 byte
                    int(sm.Graphics.tc_level) & 0xFF,               # 1 byte
                    float(sm.Physics.brake_bias),                   # 4 bytes
                    int(sm.Graphics.position),                      # 2 bytes
                    int(sm.Graphics.completed_lap)                  # 2 bytes
                )

                # Calculate CRC and append it to the data
                crc = calculate_crc(data)
                data += struct.pack('B', crc)

                # Send packed data with CRC
                arduino.write(data)
            else:
                # Send disconnection signal - single byte
                arduino.write(struct.pack('!B', 0xFF))

            # Read and process Arduino commands
            while arduino.in_waiting == 0:  # Wait for bytes to be available
                time.sleep(0.001)
            if arduino.in_waiting >= 2:  # Check if at least 2 bytes are available
                command = arduino.read(2)  # Read exactly 2 bytes
                try:
                    button_state = struct.unpack('<H', command)[0]
                    j.data.lButtons = button_state
                    j.update()
                except struct.error:
                    print("Error unpacking command")
            else:
                command = None  # No data available

    # logic for the listener in h5 files
    if sm is not None:
        # Append sector times during the lap
        if sm.Graphics.current_sector_index != current_sector:
            current_sector = sm.Graphics.current_sector_index
            sectors.append(sm.Graphics.current_time)
            print(Fore.YELLOW + "--- Sector Completed ---" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Sector Index: {current_sector}" + Style.RESET_ALL)
            print(Fore.YELLOW + f"Sector Time: {sm.Graphics.current_time:.2f}s" + Style.RESET_ALL)

        # Handle the change of tyres and the number of laps on a tyre set
        if sm.Graphics.current_tyre_set == current_tyre_set:
            number_lap_tyre += 1
        else:
            current_tyre_set = sm.Graphics.current_tyre_set
            number_lap_tyre = 1
            print(Fore.CYAN + "--- Tyre Set Changed ---" + Style.RESET_ALL)
            print(Fore.CYAN + f"New Tyre Set: {current_tyre_set}" + Style.RESET_ALL)
            print(Fore.CYAN + "Lap Count Reset" + Style.RESET_ALL)

        # Create a new HDF5 file at the beginning of a new lap
        if current_lap != sm.Graphics.completed_lap:

            os.system('cls' if os.name == 'nt' else 'clear')

            current_lap = sm.Graphics.completed_lap
            current_sector = sm.Graphics.current_sector_index
            current_start_distance = sm.Graphics.distance_traveled
            current_start_time = sm.Graphics.current_time

            h5_filename = f"lap_{current_lap}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.h5"
            current_h5_filepath = os.path.join("telemetry_data", h5_filename)
            os.makedirs("telemetry_data", exist_ok=True)
            current_h5_file = h5py.File(current_h5_filepath, "w")

            if current_h5_file:
                # Push accumulated data into the HDF5 file
                for key, data in telemetry_data.items():
                    current_h5_file.create_dataset(key, data=np.array(data))
                current_h5_file.close()  # Close the previous file

            # Reset telemetry data for the new lap
            telemetry_data = {key: [] for key in telemetry_data}

            print(Fore.GREEN + "--- New Lap Started ---" + Style.RESET_ALL)
            print(Fore.GREEN + f"Lap Number: {current_lap}" + Style.RESET_ALL)
            print(Fore.GREEN + f"HDF5 File Created: {h5_filename}" + Style.RESET_ALL)

            print(Fore.MAGENTA + "--- Sector Times ---" + Style.RESET_ALL)
            for i, sector_time in enumerate(sectors):
                print(Fore.MAGENTA + f"Sector {i+1}: {sector_time:.2f}s" + Style.RESET_ALL)

            # Format sector times
            if len(sectors) >= 3:
                sectors = [
                    sectors[0],
                    sectors[1] - sectors[0],
                    sm.Graphics.last_time - sectors[1]
                ]

                print(Fore.BLUE + "--- Formatted Sector Times ---" + Style.RESET_ALL)
                print(Fore.BLUE + f"Sector 1: {sectors[0]:.2f}s" + Style.RESET_ALL)
                print(Fore.BLUE + f"Sector 2: {sectors[1]:.2f}s" + Style.RESET_ALL)
                print(Fore.BLUE + f"Sector 3: {sectors[2]:.2f}s" + Style.RESET_ALL)

            # Add HDF5 file path to the Lap object
            info_lap = {
                'session': Session.objects.all().order_by('id').last(),
                'time': sm.Graphics.last_time,
                'compound': Compound.objects.get(name='dry_compound'),
                'date': datetime.date.today(),
                'air_temp': sm.Physics.air_temp,
                'road_temp': sm.Physics.road_temp,
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
                'sector1': sectors[0] if len(sectors) >= 1 else None,
                'sector2': sectors[1] if len(sectors) >= 2 else None,
                'sector3': sectors[2] if len(sectors) >= 3 else None,
                'tc_level': sm.Graphics.tc_level,
                'abs_level': sm.Graphics.abs_level,
                'engine_map': sm.Graphics.engine_map,
                'valid_lap': sm.Graphics.is_valid_lap,
                'tyre_set': current_tyre_set,
                'telemetry_file': current_h5_filepath  # New field for the HDF5 file
            }
            Lap.objects.create(**info_lap)

            sectors = []  # Reset sectors for the new lap

            if redis:
                #send data to channel for follow session
                async_to_sync(channel_layer.group_send)(
                    "follow-session",
                    {
                        "type": "add.lap",
                        "id": Lap.objects.filter(session=Session.objects.all().order_by('id').last()).count()+1,
                        "time": sm.Graphics.last_time,
                        "temp": sm.Physics.air_temp,
                        "fuel": sm.Physics.fuel,
                        "compound": "dry_compound",
                        "session_id": Session.objects.all().order_by('id').last().id,
                        "lap_number": sm.Graphics.completed_lap,
                        "track": Lap.objects.all().order_by('id').last().session.track.name,
                        "driver": Lap.objects.all().order_by('id').last().session.driver.name,
                    },
                )
                print(Fore.GREEN + f"New lap started: Lap {current_lap}. HDF5 file created." + Style.RESET_ALL)

        # Add telemetry data to the NumPy arrays
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
        telemetry_data["slip_ratio"].append([
            sm.Physics.slip_ratio.front_left,
            sm.Physics.slip_ratio.front_right,
            sm.Physics.slip_ratio.rear_left,
            sm.Physics.slip_ratio.rear_right
        ])
        telemetry_data["slip_angle"].append([
            sm.Physics.slip_angle.front_left,
            sm.Physics.slip_angle.front_right,
            sm.Physics.slip_angle.rear_left,
            sm.Physics.slip_angle.rear_right
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



