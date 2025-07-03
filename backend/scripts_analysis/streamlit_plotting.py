import streamlit as st
import h5py
import os
import django
import sys
import plotly.graph_objects as go
import numpy as np
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Lap, Track
from scripts_analysis.analysis_utils import rolling_average, remove_outliers, common_distance_serie
from scripts_analysis.inertial_mapping import inertial_mapping  # Importing inertial mapping function
from enum import Enum

def plot_telemetry_data(key, file_path1, file_path2=None):
    """
    Structure for the key argument: the goal is to allow the user to have different plot with the same options and to allow multiple datas in a same plot.
    key is a list of list, the first list corresponds to each plot in this section and each element of the lsit is a list containing all the data plotted in the graph.
    """
    # Generate a unique identifier for this plot
    plot_id = f"{key}_{hash(file_path1)}"
    
    # Create options for data processing
    st.write(f"## {key.capitalize()} Telemetry Data")
    options = st.expander(f"Options")
    with options:
        cols = st.columns(1)
        with cols[0]:
            st.write("### Filtering Options")    
            filtering = st.checkbox("Low bandwidth filtering ?", value=False, key=f'low_bandwidth_filtering_{plot_id}')
            if filtering:
                width = st.slider("Window size for rolling average", min_value=10, max_value=1000, value=50, key=f'rolling_average_window_size_{plot_id}')
            outliers = st.checkbox("Remove outliers ?", value=False, key=f'remove_outliers_{plot_id}')
            if outliers:
                threshold = st.slider("Number of Neighbors for LOF", min_value=1, max_value=50, value=3, key=f'outlier_threshold_{plot_id}')

    # prepare data for plotting
    # data_series = [] # is a list of all the plots in this graph, each element is a tuple (data_serie, distance_serie)
    multiple_lap_plot = False
    nb_outliers = 0
    interpolation_method = "first_as_reference"  # Default interpolation method
    try:
        # Check if we're plotting time variance
        if key == 'time_variance':
            # Time variance requires two laps for comparison
            if file_path2 is None:
                st.warning("Time variance requires two laps for comparison. Please select a second lap to compare.")
                return
                
            print('Plot Time Variance')
            with h5py.File(file_path1, 'r') as h5_file, h5py.File(file_path2, 'r') as h5_file2:
                # Get time data from both laps
                time1 = h5_file['time'][:-20]
                time2 = h5_file2['time'][:-20]
                distance1 = h5_file['distance'][:-20]
                distance2 = h5_file2['distance'][:-20]
                
                # Add interpolation method selection
                with options:
                    interpolation_method = st.selectbox(
                        "Interpolation Method",
                        ["first_as_reference", "union", "intersection"],
                        format_func=lambda x: {
                            "first_as_reference": "Use first lap as reference",
                            "union": "Use all distance points from both laps",
                            "intersection": "Use only common distance points"
                        }[x],
                        key=f'interpolation_method_{key}'
                    )
                
                # Use common_distance_serie to get aligned data
                common_distances, time1_common, time2_common = common_distance_serie(
                    np.array(distance1), 
                    np.array(time1), 
                    np.array(distance2), 
                    np.array(time2),
                    method=interpolation_method
                )
                
                # Calculate time variance
                main_data = time1_common - time2_common
                distance_data = common_distances
                
                if filtering:
                    raw_data = main_data.copy()
                    main_data = rolling_average(main_data, window_size=width)
                if outliers:
                    main_data, nb_outliers = remove_outliers(main_data, n_neighbors=threshold)
                    
                # Time variance is always a comparison plot
                multiple_lap_plot = True
        else:
            # Standard telemetry data - single lap
            with h5py.File(file_path1, 'r') as h5_file:
                main_data = h5_file[key][:]
                distance_data = h5_file['distance'][:]

                if filtering:
                    raw_data = main_data.copy()
                    main_data = rolling_average(main_data, window_size=width)
                if outliers:
                    main_data, nb_outliers = remove_outliers(main_data, n_neighbors=threshold)

            # Second lap selected, comparison between two laps
            if file_path2:
                multiple_lap_plot = True
                with h5py.File(file_path2, 'r') as h5_file2:
                    main_data2 = h5_file2[key][:]
                    distance_data2 = h5_file2['distance'][:]

                    if filtering:
                        raw_data2 = main_data2.copy()
                        main_data2 = rolling_average(main_data2, window_size=width)
                    if outliers:
                        main_data2, nb_outliers2 = remove_outliers(main_data2, n_neighbors=threshold)
                    
        # plotting
        fig = go.Figure()
        
        if key == 'time_variance':
            # Time variance plot using interpolated data
            fig.add_trace(go.Scatter(
                x=distance_data, 
                y=main_data, 
                mode='lines', 
                name=f'Time Variance (Lap 1 - Lap 2)',
                line=dict(color='purple', width=2)
            ))
            
            # Add zero line for reference
            fig.add_trace(go.Scatter(
                x=[min(distance_data), max(distance_data)],
                y=[0, 0],
                mode='lines',
                name='Reference',
                line=dict(color='black', width=1, dash='dash')
            ))
            
            fig.update_layout(
                title=f"Time Variance - {interpolation_method.replace('_', ' ').title()}",
                xaxis_title="Distance (m)",
                yaxis_title="Time Difference (s)",
                yaxis=dict(zeroline=True)
            )
        elif multiple_lap_plot:
            # Regular comparison plot without interpolation
            fig.add_trace(go.Scatter(x=distance_data, y=main_data, mode='lines', name=f'{key.capitalize()} Lap 1'))
            fig.add_trace(go.Scatter(x=distance_data2, y=main_data2, mode='lines', name=f'{key.capitalize()} Lap 2'))
            if filtering:
                fig.add_trace(go.Scatter(x=distance_data, y=raw_data, mode='lines', name=f'{key.capitalize()} Lap 1 (Raw)', line=dict(dash='dash')))
                fig.add_trace(go.Scatter(x=distance_data2, y=raw_data2, mode='lines', name=f'{key.capitalize()} Lap 2 (Raw)', line=dict(dash='dash')))
            fig.update_layout(
                title="Telemetry Data Comparison",
                xaxis_title="Distance (m)",
                yaxis_title=f"{key.capitalize()} (units)",
            )
        else:
            # Single lap plot
            fig.add_trace(go.Scatter(x=distance_data, y=main_data, mode='lines', name=key.capitalize()))
            if filtering:
                fig.add_trace(go.Scatter(x=distance_data, y=raw_data, mode='lines', name=f'{key.capitalize()} (Raw)', line=dict(dash='dash')))
            fig.update_layout(
                title="Telemetry Data",
                xaxis_title="Distance (m)",
                yaxis_title=f"{key.capitalize()} (units)",
            )

        st.plotly_chart(fig)
        if outliers:
            st.write(f"Number of outliers removed: {nb_outliers}")
        st.divider()
    except Exception as e:
        st.error(f"Error plotting telemetry data for {key}: {str(e)}")
        import traceback
        print(traceback.format_exc())


def plot_multiaxis_telemetry(key, file_path1):
    # Generate a unique identifier for this plot
    plot_id = f"multi_{key}_{hash(file_path1)}"
    
    st.write(f"## {key.capitalize()} Multi-Axis Telemetry Data")
    with st.expander(f"Options"):
        cols = st.columns(2)
        
        with cols[0]:
            st.write("### Filtering Options")
            filtering = st.checkbox("Low bandwidth filtering ?", value=False, key=f'low_bandwidth_filtering_{plot_id}')
            if filtering:
                width = st.slider("Window size for rolling average", min_value=10, max_value=1000, value=50, key=f'rolling_average_window_size_{plot_id}')
            outlier = st.checkbox("Remove outliers ?", value=False, key=f'remove_outliers_{plot_id}')
            if outlier:
                threshold = st.slider("Number of Neighbors for LOF", min_value=1, max_value=50, value=3, key=f'outlier_threshold_{plot_id}')

    try:
        with h5py.File(file_path1, 'r') as h5_file:
            if key not in h5_file:
                st.error(f"Data key '{key}' not found in telemetry file")
                return
                
            main_data = h5_file[key][:]
            if len(main_data.shape) < 2:
                st.warning(f"Data key '{key}' is not multi-axis data. Shape: {main_data.shape}")
                return
                
            data_axis = [main_data[:, i] for i in range(main_data.shape[1])]  # Initialize a list to hold data for each axis
            nb_outliers = [0 for i in range(main_data.shape[1])]  # Initialize a list to hold the number of outliers for each axis
            if filtering:
                for i in range(main_data.shape[1]):
                    data_axis[i] = rolling_average(main_data[:, i], window_size=width)
            if outlier:
                for i in range(main_data.shape[1]):
                    data_axis[i], nb_outliers[i] = remove_outliers(np.array(data_axis[i]).flatten(), n_neighbors=threshold)
            distance_data = h5_file['distance'][:]

        # Offer the possibility to display only certain axes
        with cols[1]:
            st.write("### Select Axes to Display")
            display_axes = []
            for i in range(main_data.shape[1]):
                display_axes.append(st.checkbox(f"Display Axis {i+1}", value=True, key=f'axis_{i+1}_{plot_id}'))

        fig = go.Figure()
        axis_colors = ['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'black']
        
        for i in range(main_data.shape[1]):
            if i < len(display_axes) and display_axes[i]:
                color = axis_colors[i % len(axis_colors)]
                fig.add_trace(go.Scatter(
                    x=distance_data, 
                    y=data_axis[i], 
                    mode='lines', 
                    name=f"{key.capitalize()} Axis {i+1}",
                    line=dict(color=color, width=2)
                ))
                
        fig.update_layout(
            title="Multi-axis Telemetry Data",
            xaxis_title="Distance (m)",
            yaxis_title=f"{key.capitalize()} (units)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig)
        if outlier:
            for i, nb in enumerate(nb_outliers):
                if i < len(display_axes) and display_axes[i]:
                    st.write(f"Number of outliers removed from Axis {i+1}: {nb}")
        st.divider()
    except Exception as e:
        st.error(f"Error plotting multi-axis telemetry data for {key}: {str(e)}")
        import traceback
        print(traceback.format_exc())

def plot_scatter_data(x_key, y_key, file_path1, lap_id):
    st.write(f"## Scatter Plot of {x_key.capitalize()} vs {y_key.capitalize()} for lap {lap_id}")
    with st.expander(f"Options"):
        st.write("### Plot between beacons")
        beacon_filtering = st.checkbox("Filter by beacons", value=False, key=f'beacon_filtering_{x_key}_{y_key}')
    
    try:
        with h5py.File(file_path1, 'r') as h5_file:
            # Handle x_key data
            if x_key in h5_file:
                x_data = h5_file[x_key][:]
            elif x_key[-2] == "_" and x_key[-1].isdigit(): # Handle case where x_key is like 'speed_0', getting the corresponding axis
                base_key = x_key[:-2]
                axis = int(x_key[-1])
                if base_key in h5_file and axis < h5_file[base_key][:].shape[1]:
                    x_data = h5_file[base_key][:, axis]
                else:
                    st.error(f"{x_key} not found in telemetry data.")
                    return
            else:
                st.error(f"{x_key} not found in telemetry data.")
                return
            
            # Handle y_key data
            if y_key in h5_file:
                y_data = h5_file[y_key][:]
            elif y_key[-2] == "_" and y_key[-1].isdigit():
                base_key = y_key[:-2]
                axis = int(y_key[-1])
                if base_key in h5_file and axis < h5_file[base_key][:].shape[1]:
                    y_data = h5_file[base_key][:, axis]
                else:
                    st.error(f"{y_key} not found in telemetry data.")
                    return
            else:
                st.error(f"{y_key} not found in telemetry data.")
                return

            # Filter by beacons if requested
            if beacon_filtering:
                try:
                    lap_track = Lap.objects.filter(id=lap_id).first().session.track
                    beacons = json.loads(Track.objects.filter(name=lap_track.name).first().lap_beacons)
                    
                    if not beacons:
                        st.warning("No beacons defined for this track.")
                        beacon_filtering = False
                    else:
                        start_beacon = st.selectbox(
                            "Start Beacon",
                            options=[beacon for beacon in beacons.keys()],
                            key=f'start_beacon_select_{x_key}_{y_key}',
                            index=0
                        )
                        end_beacon = st.selectbox(
                            "End Beacon",
                            options=[beacon for beacon in beacons.keys()],
                            key=f'end_beacon_select_{x_key}_{y_key}',
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
                except Exception as e:
                    st.error(f"Error with beacon filtering: {str(e)}")
                    beacon_filtering = False
                    
        # Create the plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_data, 
            y=y_data, 
            mode='markers', 
            name=f"{x_key.capitalize()} vs {y_key.capitalize()}",
            marker=dict(
                size=5,
                color=np.arange(len(x_data)),  # Color by point index for sequential coloring
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sequence")
            )
        ))
        fig.update_layout(
            title=f"{x_key.capitalize()} vs {y_key.capitalize()}",
            xaxis_title=x_key.capitalize(),
            yaxis_title=y_key.capitalize(),
        )
        st.plotly_chart(fig)
        st.divider()
    except Exception as e:
        st.error(f"Error creating scatter plot: {str(e)}")
        import traceback
        print(traceback.format_exc())

def render_inertial_mapping(lap_id, key='speed'):
    st.write(f"## Inertial mapping (colored by {key.capitalize()})")
    try:
        lap = Lap.objects.get(id=lap_id)
        position, speed, beacon_position = inertial_mapping(lap.id)
        
        # Check if position is empty - properly handle arrays
        if position is None or (isinstance(position, list) and len(position) == 0):
            st.error(f"No position data available for lap {lap_id}")
            return
            
        with h5py.File(lap.telemetry_file.path, 'r') as h5_file:
            if key in h5_file:
                color_data = h5_file[key][:]
            elif key[-2] == "_" and key[-1].isdigit(): # Handle case where x_key is like 'speed_0', getting the corresponding axis
                base_key = key[:-2]
                axis = int(key[-1])
                if base_key in h5_file and axis < h5_file[base_key][:].shape[1]:
                    color_data = h5_file[base_key][:, axis]
                else:
                    st.error(f"{key} not found in telemetry data.")
                    return
            else:
                st.error(f"{key} not found in telemetry data.")
                return
        
        # Ensure color_data is the right length
        if len(color_data) > len(position):
            color_data = color_data[:len(position)]
        elif len(color_data) < len(position):
            # Pad with last value if needed
            color_data = np.pad(color_data, (0, len(position) - len(color_data)), 'edge')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[float(pos[1]) for pos in position],
            y=[float(pos[2]) for pos in position],
            mode='lines+markers',
            name='Track Layout',
            marker=dict(
                size=5,
                color=color_data,
                colorscale='Viridis',
                colorbar=dict(title=key.capitalize()),
                showscale=True
            ),
            line=dict(width=3, color='rgba(0,0,0,0.1)')
        ))
        
        # Safely check beacon_position
        if beacon_position is not None and (isinstance(beacon_position, list) and len(beacon_position) > 0):
            fig.add_trace(go.Scatter(
                x=[float(pos[1]) for pos in beacon_position],
                y=[float(pos[2]) for pos in beacon_position],
                mode='markers',
                name='Beacons',
                marker=dict(color='red', size=7, symbol='circle'),
            ))
            
        fig.update_layout(
            title=f"Trajectory for Lap {lap_id}",
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
            ),
        )
        st.plotly_chart(fig, use_container_width=False)
    except Exception as e:
        st.error(f"Error rendering inertial mapping: {str(e)}")
        import traceback
        print(traceback.format_exc())
