import os
import django
import numpy as np
import h5py
import matplotlib.pyplot as plt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track

def traction_circle(lap_id):
    '''
    Plot the traction circle of the lap.
    '''

    lap = Lap.objects.get(id=lap_id)

    with h5py.File(lap.telemetry_file.path, 'r') as f:
        g_lat = f['g_force'][:, 0]
        g_long = f['g_force'][:, 1]

        plt.scatter(g_lat, g_long)
        plt.grid()
        plt.show()
