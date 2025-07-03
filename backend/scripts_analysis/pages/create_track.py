"""
Script that uses the Streamlit library to create a track
This script is used to create a track in the database.
"""

import streamlit as st
import plotly.graph_objects as go
import json

import os
import django
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Track, Lap
from scripts_analysis.inertial_mapping import inertial_mapping

def create_track():
    track = Track.objects.create(
        name=track_name,
        location=track_location,
        length=track_length,
        country=track_country,
        turn=track_turn
    )
    track.save()
    pass

st.set_page_config(page_title="Track Creation", page_icon=":checkered_flag:", layout="wide")

st.title("Create a Track")
st.write("This is where you can create a track in the database.")

track_name = st.text_input("Track Name")
track_location = st.text_input("Track Location")
track_length = st.number_input("Track Length (km)", min_value=0.1, max_value=100.0)
track_country = st.text_input("Track Country")
track_turn = st.number_input("Number of Turns", min_value=1, max_value=50)

st.button("Create Track", on_click=create_track)

st.divider()

st.write("## Set beacon for a track")

modified_track = st.selectbox("Select Track", Track.objects.all(), format_func=lambda x: x.name)

if modified_track:
    # Display the layout of the track with the inertial mapping of the fastest lap
    try:
        lap = Lap.objects.filter(session__track=modified_track, valid_lap=True).order_by('time').first()
        position, speed, beacon_position = inertial_mapping(lap.id)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[pos[1] for pos in position],
            y=[pos[2] for pos in position],
            mode='lines',
            name='Track Layout',
        ))
        fig.add_trace(go.Scatter(
            x=[pos[1] for pos in beacon_position],
            y=[pos[2] for pos in beacon_position],
            mode='markers',
            name='Beacons',
            marker=dict(color='red', size=7, symbol='circle'),
        ))
        fig.update_layout(
            title=f"Track Layout for {modified_track.name}",
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
            ),
        )
        st.plotly_chart(fig, use_container_width=False)
    except AttributeError as e:
        st.error("No lap recorded for this track, it is not possible to show the layout...")

    beacons = json.loads(modified_track.lap_beacons)
    cols = st.columns(2)
    with cols[0]:  
        input_position = []
        for i, beacon in enumerate(beacons.keys()):
            st.write(f"### Beacon {i + 1}: {beacon.capitalize()}")
            input_position.append(st.number_input("Position", key=f"beacon_{i}", value=int(beacons[beacon]), step=1))
        if st.button("Update Beacons"):
            if all(pos >= 0 for pos in input_position):
                beacons = {name: pos for name, pos in zip(beacons.keys(), input_position)}
                modified_track.lap_beacons = json.dumps(beacons)
                modified_track.save()
                st.success(f"Beacons updated for {modified_track.name}")
                st.rerun()
            else:
                st.error("All beacon positions must be non-negative integers.")

    with cols[1]:
        st.write("### Add a new beacon")
        new_beacon_name = st.text_input("New Beacon Name")
        new_beacon_position = st.number_input("New Beacon Position", min_value=0, step=1)
        if st.button("Add Beacons"):
            if new_beacon_name:
                beacons[new_beacon_name] = new_beacon_position
                modified_track.lap_beacons = json.dumps(beacons)
                modified_track.save()
                st.success(f"Beacons updated for {modified_track.name}")
                st.rerun()
            else:
                st.error("Please enter a name for the new beacon.")
