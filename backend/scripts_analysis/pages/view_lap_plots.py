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
from scripts_analysis.inertial_mapping import inertial_mapping  # Importing inertial mapping function
from enum import Enum

from scripts_analysis.streamlit_plotting import plot_multiaxis_telemetry, plot_telemetry_data, plot_scatter_data, render_inertial_mapping

class DisplayMode(Enum):
    PLOT="plot"
    SCATTER="scatter"
    MAP="map"

# Save initial plots in a separate variable
default_plots = [
    {"type": DisplayMode.MAP, "data": "speed"},
    {"type": DisplayMode.SCATTER, "data_x": "g_force_0", "data_y": "g_force_1"},
    {"type": DisplayMode.PLOT, "data": "speed"},
    {"type": DisplayMode.PLOT, "data": "tyre_pressure"}
]

if 'studied_lap_id' not in st.session_state:
    # Initialize the studied lap ID to the first lap in the database
    st.session_state['studied_lap_id'] = Lap.objects.first().id if Lap.objects.exists() else None

# Initialize session state for plots with default values if not already set
if 'plots' not in st.session_state:
    st.session_state["plots"] = default_plots.copy()
    
# Always backup plots right after checking or initializing them
if 'plots_backup' not in st.session_state or st.session_state["plots"] != st.session_state.get("plots_backup", []):
    st.session_state["plots_backup"] = st.session_state["plots"].copy()
    
def restore_plots():
    """Restore plots from backup if needed"""
    if "plots_backup" in st.session_state and (not st.session_state["plots"] or len(st.session_state["plots"]) == 0):
        st.session_state["plots"] = st.session_state["plots_backup"].copy()
        
# Call restore at the beginning to ensure plots are restored if needed
restore_plots()


def view_lap_plots(plots_list):
    # st.session_state.setdefault('studied_lap_id', Lap.objects.first().id)
    selected_lap = st.selectbox(
        "Select Lap",
        list(Lap.objects.all()),
        format_func=lambda x: f"{x.id} - {x.session.car.name} on {x.session.track.name} ({x.session.date})",
        index=(list(Lap.objects.all()).index(Lap.objects.get(id=st.session_state.studied_lap_id)) if 'studied_lap_id' in st.session_state else 0),
        key='first_lap_select',
        on_change=lambda: setattr(st.session_state, 'studied_lap_id', selected_lap.id if selected_lap else Lap.objects.first().id)    )
    compared_lap = st.selectbox(
        "Compare with another Lap (optional)",
        [None] + list(Lap.objects.all()),
        format_func=lambda x: f"{x.id} - {x.session.car.name} on {x.session.track.name} ({x.session.date})" if x else "None",
        key='second_lap_select'
    )
    
    if compared_lap and selected_lap.id == compared_lap.id:
        st.error("You cannot compare a lap with itself. Please select a different lap for comparison.")
        return
        
    if not selected_lap.telemetry_file:
        st.write("No telemetry file available for this lap.")
        return
        
    # Display the title
    if compared_lap and compared_lap.telemetry_file:
        st.write(f"# Comparing Lap {selected_lap.id} with Lap {compared_lap.id}")
        st.write(f"For multiaxis plots, only the data of {selected_lap.id} will be displayed.")
    else:
        st.write(f"# Telemetry Data for Lap {selected_lap.id}")
    
    # Render all plots from the session state
    if not plots_list or len(plots_list) == 0:
        st.warning("No plots to display. Add plots using the sidebar controls.")
        return
        
    # Iterate through each plot in the session state
    for data_type in plots_list:
        try:
            with h5py.File(selected_lap.telemetry_file.path, 'r') as h5_file:
                plot_type = data_type["type"].value
                # Handle plot type comparison for both Enum and string values
                    
                if plot_type == DisplayMode.PLOT.value:
                    # Check if data exists in the H5 file before plotting
                    if data_type["data"] not in h5_file:
                        st.error(f"Data key '{data_type['data']}' not found in telemetry file")
                        continue
                    
                    if len(h5_file[data_type["data"]][:].shape) > 1:  # Check if data has multiple dimensions
                        plot_multiaxis_telemetry(data_type["data"], selected_lap.telemetry_file.path)
                    else:
                        plot_telemetry_data(data_type["data"], selected_lap.telemetry_file.path, 
                                          compared_lap.telemetry_file.path if compared_lap and compared_lap.telemetry_file else None)
                elif plot_type == DisplayMode.SCATTER.value:
                    plot_scatter_data(data_type["data_x"], data_type["data_y"], selected_lap.telemetry_file.path, selected_lap.id)
                elif plot_type == DisplayMode.MAP.value:
                    render_inertial_mapping(selected_lap.id, key=data_type["data"])
                else:
                    st.error(f"Unknown plot type: {plot_type_value}")
                    continue
        except KeyError as ke:
            st.error(f"Missing data key: {ke}")
            continue
        except Exception as e:
            st.error(f"Error rendering plot: {str(e)}")
            import traceback
            print(traceback.format_exc())
            continue


st.set_page_config(page_title="Lap Telemetry Viewer", page_icon=":chart_with_upwards_trend:", layout="wide")

st.title("View Lap Telemetry Plots")
st.write("Select a lap to view telemetry plots.")

with st.sidebar:
    st.write("### Add a plot:")
    # Generate a unique key for each interaction
    interaction_id = st.session_state.get('interaction_id', 0)
    
    type_of_plot = st.radio("Select the type of plot you want to add",
        [
            DisplayMode.PLOT,
            DisplayMode.SCATTER,
            DisplayMode.MAP
        ],
        format_func=lambda x: x.value.capitalize(),
        key=f'plot_type_select_{interaction_id}',
    )
    if type_of_plot == DisplayMode.PLOT:
        st.write("### Choose the data you want to visualize")
        data_selected = st.radio("Select Telemetry Data",
            [
                'speed',
                'throttle',
                'brake',
                'steering_angle',
                'rpm',
                'g_force',
                'suspension_travel',
                'slip_angle',
                'tyre_pressure'
            ],
            format_func=lambda x: x.capitalize(),
            key=f'telemetry_data_select_{interaction_id}',
            index=0
        )
    elif type_of_plot == DisplayMode.SCATTER:
        st.write("### Choose the data you want to visualize")
        data_selected_1 = st.radio("Select X-Axis Data",
            [
                'g_force_0',
                'g_force_1',
                'speed',
                'throttle',
                'brake',
                'steering_angle',
                'rpm',
                "distance"
            ],
            format_func=lambda x: x.capitalize(),
            key=f'telemetry_data_select_x_{interaction_id}',
            index=0
        )
        data_selected_2 = st.radio("Select Y-Axis Data",
            [
                'g_force_0',
                'g_force_1',
                'speed',
                'throttle',
                'brake',
                'steering_angle',
                'rpm'
            ],
            format_func=lambda x: x.capitalize(),
            key=f'telemetry_data_select_y_{interaction_id}',
            index=1
        )
    elif type_of_plot == DisplayMode.MAP:
        st.write("### Show the data you want to visualize")
        data_selected = st.radio("Select Color Scale Data",
            [
                'speed',
                'g_force_0',
                'g_force_1',
                'throttle',
                'brake',
                'steering_angle',
            ],
            format_func=lambda x: x.capitalize(),
            key=f'telemetry_data_select_map_{interaction_id}',
            index=0
        )
        
    if st.button("Add Plot", key=f'add_plot_button_{interaction_id}'):
        # Increment interaction ID for next time
        st.session_state['interaction_id'] = interaction_id + 1
        
        if type_of_plot == DisplayMode.PLOT:
            st.session_state["plots"].append({
                "type": DisplayMode.PLOT,
                "data": data_selected
            })
        elif type_of_plot == DisplayMode.SCATTER:
            st.session_state["plots"].append({
                "type": DisplayMode.SCATTER,
                "data_x": data_selected_1,
                "data_y": data_selected_2
            })
        elif type_of_plot == DisplayMode.MAP:            
            st.session_state["plots"].append({
                "type": DisplayMode.MAP,
                "data": data_selected
            })
        # Update backup
        st.session_state["plots_backup"] = st.session_state["plots"].copy()
        st.rerun()      # Display the current plots in the sidebar with removal buttons
    if st.session_state["plots"]:
        st.write("### Current Plots:")
        plots_to_remove = []
        
        # Use columns to display plot name and removal button side by side
        for i, plot in enumerate(st.session_state["plots"]):
            col1, col2 = st.columns([4, 1])
            with col1:
                try:
                    # Handle both Enum and string value cases
                    plot_type_value = plot["type"].value                        
                    if plot_type_value == DisplayMode.PLOT.value:
                        st.write(f"{i+1}. Plot: {plot['data'].capitalize()}")
                    elif plot_type_value == DisplayMode.SCATTER.value:
                        st.write(f"{i+1}. Scatter: {plot['data_x'].capitalize()} vs {plot['data_y'].capitalize()}")
                    elif plot_type_value == DisplayMode.MAP.value:
                        st.write(f"{i+1}. Map: {plot['data'].capitalize()}")
                    else:
                        st.write(f"{i+1}. Unknown Plot Type")
                except Exception as e:
                    st.write(f"{i+1}. Invalid Plot Format: {str(e)}")
            with col2:
                if st.button("❌", key=f"remove_plot_{i}"):
                    plots_to_remove.append(i)
        
        # Remove plots that were marked for removal
        if plots_to_remove:
            for idx in sorted(plots_to_remove, reverse=True):
                st.session_state["plots"].pop(idx)
            st.session_state["plots_backup"] = st.session_state["plots"].copy()
            st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset to Default"):
                st.session_state["plots"] = default_plots.copy()
                st.session_state["plots_backup"] = st.session_state["plots"].copy()
                st.rerun()
        with col2:
            if st.button("Clear All"):
                st.session_state["plots"] = []
                st.session_state["plots_backup"] = st.session_state["plots"].copy()
                st.rerun()

view_lap_plots(st.session_state["plots"])

# Debugging information (only visible in terminal/logs)
print(f"Number of plots in session_state: {len(st.session_state['plots'])}")
print(f"Plots: {st.session_state['plots']}")
