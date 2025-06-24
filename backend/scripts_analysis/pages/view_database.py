"""
Script that uses the Streamlit library to visualize database entries
This script allows users to select a model and view all entries with detailed information.
"""

import streamlit as st

import os
import django
import sys

from scripts_analysis.utils import format_lap_time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Driver, Car, Track, Session, Lap

MODEL_CHOICES = {
    "Driver": Driver,
    "Car": Car,
    "Track": Track,
    "Session": Session,
    "Lap": Lap
}

def view_database():
    selected_model = st.selectbox("Select Model", list(MODEL_CHOICES.keys()))
    model = MODEL_CHOICES[selected_model]

    if selected_model == "Lap":
        selected_track = st.selectbox("Filter by Track", [None] + list(Track.objects.all()), format_func=lambda x: x.name if x else "All Tracks")
        selected_car = st.selectbox("Filter by Car", [None] + list(Car.objects.all()), format_func=lambda x: x.name if x else "All Cars")
        selected_driver = st.selectbox("Filter by Driver", [None] + list(Driver.objects.all()), format_func=lambda x: x.name if x else "All Drivers")

        filters = {}
        if selected_track:
            filters['session__track'] = selected_track
        if selected_car:
            filters['session__car'] = selected_car
        if selected_driver:
            filters['session__driver'] = selected_driver

        entries = model.objects.filter(**filters)
    else:
        entries = model.objects.all()

    if entries.exists():
        st.write(f"### {selected_model} Entries")
        for entry in entries:
            st.write("---")
            if selected_model == "Lap":
                st.write(f"**Lap ID**: {entry.id}")
                st.write(f"**Time**: {format_lap_time(entry.time)}")
                st.write(f"**Track**: {entry.session.track.name}")
                st.write(f"**Driver**: {entry.session.driver.name}")
                st.write(f"**Car**: {entry.session.car.name}")
            else:
                for field, value in entry.__dict__.items():
                    if field != "_state":  # Exclude internal Django state field
                        st.write(f"**{field.capitalize()}**: {value}")
            if selected_model == "Lap" and entry.telemetry_file:
                if st.button(f"View Telemetry for Lap {entry.id}"):
                    st.session_state.studied_lap_id = entry.id
                    st.switch_page("pages/view_lap_plots.py")
    else:
        st.write(f"No entries found for {selected_model}.")

st.set_page_config(page_title="Database Viewer", page_icon=":mag:", layout="wide")

st.title("View Database Entries")
st.write("Select a model to view all entries in the database.")

view_database()
