"""
Script that uses the Streamlit library to visualize lap telemetry plots
This script allows users to select a lap and view plots based on telemetry data.
"""

import streamlit as st
import h5py
import os
import django
import sys
import plotly.graph_objects as go
import numpy as np
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track
from scripts_analysis.analysis_utils import rolling_average, remove_outliers
from enum import Enum

class DisplayMode(Enum):
    PLOT="plot"
    SCATTER="scatter"


display_mode = {
    "speed": DisplayMode.PLOT,
    "throttle": DisplayMode.PLOT,
    "brake": DisplayMode.PLOT,
    "steering_angle": DisplayMode.PLOT,
    "rpm": DisplayMode.PLOT,
    "g_force": DisplayMode.PLOT,
    "suspension_travel": DisplayMode.PLOT,
    "slip_angle": DisplayMode.PLOT,
    "traction_circle": DisplayMode.SCATTER,
}

def plot_telemetry_data(key, file_path1, file_path2=None):
    st.write(f"## {key.capitalize()} Telemetry Data")
    cols = st.columns(1)
    with cols[0]:
        st.write("### Filtering Options")    
        filtering = st.checkbox("Low bandwidth filtering ?", value=False, key=f'low_bandwidth_filtering_{key}')
        if filtering:
            width = st.slider("Window size for rolling average", min_value=10, max_value=1000, value=50, key=f'rolling_average_window_size_{key}')
        outliers = st.checkbox("Remove outliers ?", value=False, key=f'remove_outliers_{key}')
        if outliers:
            threshold = st.slider("Number of Neighbors for LOF", min_value=1, max_value=50, value=3, key=f'outlier_threshold_{key}')

    with h5py.File(file_path1, 'r') as h5_file:
        main_data = h5_file[key][:]
        distance_data = h5_file['distance'][:]

        if filtering:
            main_data = rolling_average(main_data, window_size=width)
        if outliers:
            main_data, nb_outliers = remove_outliers(main_data, n_neighbors=threshold)

    if file_path2:
        with h5py.File(file_path2, 'r') as h5_file2:
            main_data2 = h5_file2[key][:]
            distance_data2 = h5_file2['distance'][:]

            if filtering:
                main_data2 = rolling_average(main_data2, window_size=width)
            if outliers:
                main_data2 = remove_outliers(main_data2, threshold=threshold)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=distance_data, y=main_data, mode='lines', name=f'{key.capitalize()} Lap 1'))
            fig.add_trace(go.Scatter(x=distance_data2, y=main_data2, mode='lines', name=f'{key.capitalize()} Lap 2'))
            fig.update_layout(
                title="Telemetry Data Comparison",
                xaxis_title="Distance (m)",
                yaxis_title=f"{key.capitalize()} (units)",
            )
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=distance_data, y=main_data, mode='lines', name=key.capitalize()))
        fig.update_layout(
            title="Telemetry Data",
            xaxis_title="Distance (m)",
            yaxis_title=f"{key.capitalize()} (units)",
        )

    st.plotly_chart(fig)
    if outliers:
        st.write(f"Number of outliers removed: {nb_outliers}")
    st.divider()

def plot_multiaxis_telemetry(key, file_path1):
    st.write(f"## {key.capitalize()} Telemetry Data")
    cols = st.columns(2)
    
    with cols[0]:
        st.write("### Filtering Options")
        filtering = st.checkbox("Low bandwidth filtering ?", value=False, key=f'low_bandwidth_filtering_{key}')
        if filtering:
            width = st.slider("Window size for rolling average", min_value=10, max_value=1000, value=50, key='rolling_average_window_size')
        outlier = st.checkbox("Remove outliers ?", value=False, key=f'remove_outliers_{key}')
        if outlier:
            threshold = st.slider("Number of Neighbors for LOF", min_value=1, max_value=50, value=3, key=f'outlier_threshold_{key}')

    with h5py.File(file_path1, 'r') as h5_file:
        main_data = h5_file[key][:]
        data_axis = [main_data[:, i] for i in range(main_data.shape[1])]  # Initialize a list to hold data for each axis
        nb_outliers = [0 for i in range(main_data.shape[1])]  # Initialize a list to hold the number of outliers for each axis
        if filtering:
            for i in range(main_data.shape[1]):
                data_axis[i] = rolling_average(main_data[:, i], window_size=width)
        if outlier:
            for i in range(main_data.shape[1]):
                print(data_axis[i])
                data_axis[i], nb_outliers[i] = remove_outliers(np.array(data_axis[i]).flatten(), n_neighbors=threshold)
        distance_data = h5_file['distance'][:]

    # Offer the possibility to display only certain axes
    with cols[1]:
        st.write("### Select Axes to Display")
        display_axes = []
        for i in range(main_data.shape[1]):
            display_axes.append(st.checkbox(f"Display Axis {i+1}", value=True, key=f'axis_{i+1}'))


    fig = go.Figure()
    for i in range(main_data.shape[1]):
        if display_axes[i]:
            fig.add_trace(go.Scatter(x=distance_data, y=data_axis[i], mode='lines', name=f"{key.capitalize()} Axis {i+1}"))
    fig.update_layout(
        title="Multi-axis Telemetry Data",
        xaxis_title="Distance (m)",
        yaxis_title=f"{key.capitalize()} (units)",
    )

    st.plotly_chart(fig)
    if outlier:
        for i, nb in enumerate(nb_outliers):
            st.write(f"Number of outliers removed from Axis {i+1}: {nb}")
    st.divider()

def plot_scatter_data(x_key, y_key, file_path1, lap_id):
    st.write(f"## Scatter Plot of {x_key.capitalize()} vs {y_key.capitalize()} for lap {lap_id}")
    st.write("### Plot between beacons")
    beacon_filtering = st.checkbox("Filter by beacons", value=False, key='beacon_filtering')
    
    with h5py.File(file_path1, 'r') as h5_file:
        if x_key not in h5_file: # Check if x_key exists in the file
            if x_key[-2] == "_" and x_key[-1].isdigit(): # Handle case where x_key is like 'speed_0', getting the corresponding axis
                x_data = h5_file[x_key[:-2]][:, int(x_key[-1])]
            else:
                st.error(f"{x_key} not found in telemetry data.")
                return
        else:
            x_data = h5_file[x_key][:]
        if y_key not in h5_file:
            if y_key[-2] == "_" and y_key[-1].isdigit():
                y_data = h5_file[y_key[:-2]][:, int(y_key[-1])]
            else:
                st.error(f"{y_key} not found in telemetry data.")
                return
        else:
            y_data = h5_file[y_key][:]

        if beacon_filtering:
            beacons = json.loads(Track.objects.filter(name=Lap.objects.filter(id = lap_id).first().session.track.name).first().lap_beacons)
            start_beacon = st.selectbox(
                "Start Beacon",
                options = [beacon for beacon in beacons.keys()],
                key='start_beacon_select',
                index=0
            )
            end_beacon = st.selectbox(
                "End Beacon",
                options = [beacon for beacon in beacons.keys()],
                key='end_beacon_select',
                index=1
            )
            if start_beacon == end_beacon:
                st.error("Start and End beacons cannot be the same. Please select different beacons.")
                return
            else:
                start_distance = beacons[start_beacon]
                end_distance = beacons[end_beacon]
                if start_distance >= end_distance:
                    st.error("Start beacon distance must be less than End beacon distance. Please select different beacons.")
                    return
                mask = (h5_file['distance'][:] >= start_distance) & (h5_file['distance'][:] <= end_distance)
                x_data = x_data[mask]
                y_data = y_data[mask]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='markers', name=f"{x_key.capitalize()} vs {y_key.capitalize()}"))
    fig.update_layout(
        title=f"{x_key.capitalize()} vs {y_key.capitalize()}",
        xaxis_title=x_key.capitalize(),
        yaxis_title=y_key.capitalize(),
    )
    st.plotly_chart(fig)
    st.divider()

def view_lap_plots(type_data):
    st.session_state.setdefault('studied_lap_id', Lap.objects.first().id)
    selected_lap = st.selectbox(
        "Select Lap",
        list(Lap.objects.all()),
        format_func=lambda x: f"{x.id} - {x.session.car.name} on {x.session.track.name} ({x.session.date})",
        index=(list(Lap.objects.all()).index(Lap.objects.get(id=st.session_state.studied_lap_id)) if 'studied_lap_id' in st.session_state else 0),
        key='first_lap_select',
        on_change=lambda: setattr(st.session_state, 'studied_lap_id', selected_lap.id if selected_lap else Lap.objects.first().id)
    )
    compared_lap = st.selectbox(
        "Compare with another Lap (optional)",
        [None] + list(Lap.objects.all()),
        format_func=lambda x: f"{x.id} - {x.session.car.name} on {x.session.track.name} ({x.session.date})" if x else "None",
        key='second_lap_select'
    )
    if compared_lap and selected_lap.id == compared_lap.id:
        st.error("You cannot compare a lap with itself. Please select a different lap for comparison.")
        return

    if selected_lap.telemetry_file:
        if compared_lap and compared_lap.telemetry_file:
            st.write(f"# Comparing Lap {selected_lap.id} with Lap {compared_lap.id}")
            st.write(f"For multiaxis plots, only the data of {selected_lap.id} will be displayed.")
        else:
            st.write(f"# Telemetry Data for Lap {selected_lap.id}")
        for data_type in type_data:
            with h5py.File(selected_lap.telemetry_file.path, 'r') as h5_file:
                if display_mode[data_type] == DisplayMode.PLOT: # Plotting mode
                    if len(h5_file[data_type][:].shape) > 1:  # Check if data has multiple dimensions
                        plot_multiaxis_telemetry(data_type, selected_lap.telemetry_file.path)
                    else:
                        plot_telemetry_data(data_type, selected_lap.telemetry_file.path, compared_lap.telemetry_file.path if compared_lap and compared_lap.telemetry_file else None)
                elif display_mode[data_type] == DisplayMode.SCATTER: # Scatter plot mode
                    if data_type == 'traction_circle':
                        plot_scatter_data('g_force_0', 'g_force_1', selected_lap.telemetry_file.path, selected_lap.id)
                    else:
                        plot_scatter_data(data_type, 'distance', selected_lap.telemetry_file.path, selected_lap.id) # Default way to plot to avoid errors
    else:
        st.write("No telemetry file available for this lap.")


st.set_page_config(page_title="Lap Telemetry Viewer", page_icon=":chart_with_upwards_trend:", layout="wide")

st.title("View Lap Telemetry Plots")
st.write("Select a lap to view telemetry plots.")

with st.sidebar:
    st.write("### Choose the data you want to visualize")
    data_selected = st.multiselect("Select Telemetry Data",
        [
            'speed',
            'throttle',
            'brake',
            'steering_angle',
            'rpm',
            'g_force',
            'suspension_travel',
            'traction_circle'
        ],
        format_func=lambda x: x.capitalize(),
        key='telemetry_data_select',
        default=['traction_circle', 'speed', 'g_force']
    )

view_lap_plots(data_selected)
