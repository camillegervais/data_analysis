"""
Script that use the streamlit library to create a session
This script is used to create a session for the user to interact with the application.
"""

import streamlit as st

import os
import django
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Track, Driver, Car, Session

def create_session():
    track = Track.objects.get(name=selected_track)
    driver = Driver.objects.get(name=selected_driver)
    car = Car.objects.get(name=selected_car)
    session = Session.objects.create(
        track=track,
        driver=driver,
        car=car,
        date=selected_date,
        weather=selected_weather,
        session_type=selected_session_type
    )
    session.save()
    pass

st.set_page_config(page_title="Session Creation", page_icon=":guardsman:", layout="wide")

st.title("Create a Session")
st.write("This is where you can create a session for your interaction with the application.")

selected_track = st.selectbox("Track", [track.name for track in Track.objects.all()])
selected_driver = st.selectbox("Driver", [driver.name for driver in Driver.objects.all()])
selected_car = st.selectbox("Car", [car.name for car in Car.objects.all()])

selected_date = st.date_input("Session Date")
selected_weather = st.selectbox("Weather", ["Sunny", "Rainy", "Cloudy"])
selected_session_type = st.selectbox("Session Type", ["Practice", "Qualifying", "Race"])

# Add more functionality as needed
st.button("Create Session", on_click=create_session)