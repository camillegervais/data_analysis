import time
import h5py
import numpy as np
import os
import django
import matplotlib.pyplot as plt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track

def inertial_mapping(lap_id):
    '''
    Function to generate the speed and the position of the car throughout the lap, using the inertial mapping technique.
    Require the lap_id in the database.
    Require the library h5py to read the telemetry file and numpy to manipulate the data.
    '''
    lap = Lap.objects.get(id=lap_id)
    h5_file = h5py.File(lap.telemetry_file.path, 'r')

    speed = h5_file['speed'][:] / 3.6  # Convert speed from km/h to m/s
    g_lat = h5_file['g_force'][:, 0]
    time = h5_file['time'][:] / 100  # Convert time from ms to seconds

    # angle, x, y
    position = [[0, 0, 0]]
    delta_angle_list = []

    for i in range(len(speed)):
        if g_lat[i] != 0:
            dt = time[i] - time[i-1]
            delta_angle = (g_lat[i]/speed[i]**2) * (dt * speed[i])
            if delta_angle < 1 and delta_angle > -1:
                delta_angle_list.append(delta_angle)
            else:
                delta_angle_list.append(0)
                delta_angle = 0
        else:
            delta_angle = 0
            delta_angle_list.append(0)

        displacement = speed[i] * dt

        # filter huge displacement
        if abs(displacement) < 100:
            position.append([position[-1][0] + delta_angle, 
                                position[-1][1] + displacement * np.cos(position[-1][0] + delta_angle),
                                position[-1][2] + displacement * np.sin(position[-1][0] + delta_angle)])
        
    # Resolve the case where the final position is not the same as the initial position
    distance_vector = np.array([position[-1][1] - position[0][1], position[-1][2] - position[0][2]])
    for i in range(len(position)):
        position[i][1] -= distance_vector[0]*((i+1)/len(position))
        position[i][2] -= distance_vector[1]*((i+1)/len(position))

    h5_file.close()
    # Save the position in the h5 file
    with h5py.File(lap.telemetry_file.path, 'a') as f:
        if 'position' in f.keys():
            del f['position']
        f.create_dataset('position', data=np.array(position))
        f.close()

    print("Inertial mapping completed")

    return np.array(position), speed

def render_plot(position, speed):
    plt.scatter(position[:, 1], position[:, 2], s=0.5, c=speed[:position.shape[0]]*3.6, cmap='viridis')  # Color by speed
    plt.colorbar(label='Speed (km/h)')  # Add a colorbar to show speed scale
    plt.axis('equal')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.show()

if __name__ == "__main__":
    lap_id = 121  # Replace with the actual lap ID you want to process
    position, speed = inertial_mapping(lap_id)
    render_plot(position, speed)
