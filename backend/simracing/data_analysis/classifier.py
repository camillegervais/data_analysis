from tkinter import Y
from typing import final
from sklearn.neighbors import KNeighborsClassifier
import os
import django
import h5py
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track

def prepare_training_data(track_id):
    """
    Generate processed data for classifying for the selected track.
    The data is generated from the telemetry data stored in the database.

    Args:
        track_id (int): track_id in the database
    Returns:
        X (list): list of telemetry data for the selected track
        Y (list): list of lap types for the selected track
    """
    X = []
    Y = []
    print("Track ID: ", track_id)
    laps = Lap.objects.filter(session__track__id=track_id).exclude(lap_type__iexact='Completed').order_by('id')
    print("Laps: ", laps.count())
    for lap in laps:
        Y.append(lap.lap_type)
        # data from the lap object
        X.append([
            lap.time,
            lap.valid_lap,
            lap.sector1,
            lap.sector2,
            lap.sector3,
        ])

    
    return X, Y

def prepare_estimated_data(lap_id):
    """
    Generate processed data for classifying for the selected lap.
    The data is generated from the telemetry data stored in the database.

    Args:
        lap_id (int): lap_id in the database
    Returns:
        X (list): list of telemetry data for the selected lap
    """
    X = []

    lap = Lap.objects.get(id=lap_id)
    # data from the lap object
    X.append([
        lap.time,
        lap.valid_lap,
        lap.sector1,
        lap.sector2,
        lap.sector3,
    ])

    
    return X


def metric(lap1, lap2):
    """
    Calculate the distance between two laps.
    The distance is calculated as the Euclidean distance between the two laps, each coordinate being weighted.

    Args:
        lap1 (Lap): first lap
        lap2 (Lap): second lap

    Returns:
        float: distance between the two laps
    """
    hyper_param = [
        1,  # lap time
        1,  # valid lap
        1,  # sector 1
        1,  # sector 2
        1,  # sector 3
    ]
    return np.linalg.norm((np.array(lap1) - np.array(lap2)) * hyper_param)

def predict_lap_type(lap_id, track_id):
    """
    Predict the lap type for the selected lap.

    Args:
        lap_id (int): lap_id in the database
        track_id (int): track_id in the database

    Returns:
        str: predicted lap type
    """
    n_neighbors = 3

    X_final, Y_final = prepare_training_data(track_id)
    if len(X_final) < n_neighbors:
        return "Not enough data"
    X_test = prepare_estimated_data(lap_id)

    print("X_final: ", np.array(X_final).shape)
    print("Y_final: ", np.array(Y_final).shape)

    knn = KNeighborsClassifier(n_neighbors=n_neighbors, metric=metric)
    knn.fit(X_final, Y_final)

    return knn.predict(X_test)[0]  # Return the predicted lap type
