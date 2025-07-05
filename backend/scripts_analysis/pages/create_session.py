"""
Script that use the streamlit library to create a session
This script is used to create a session for the user to interact with the application.
"""

import streamlit as st

import os
import django
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Track, Driver, Car, Session, Lap

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

st.divider()

st.write("# Current Session")

last_session = Session.objects.last()
if last_session:
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Track**: {last_session.track.name}")
        st.write(f"**Driver**: {last_session.driver.name}")
        st.write(f"**Car**: {last_session.car.name}")
        st.write(f"**Number of laps**: {Lap.objects.filter(session=last_session).count()}")
    with col2:
        st.write(f"**Date**: {last_session.date}")
        st.write(f"**Weather**: {last_session.weather}")
        st.write(f"**Session Type**: {last_session.session_type}")
        wheel = st.checkbox("Use steering wheel", key='steering_wheel', value=True)
        redis = st.checkbox("Use Redis", key='redis', value=False)
        listener = st.button("Launch Listener", key="launch_listener")
    comments = st.text_area("Comments", value=last_session.comments, key="comments")
    if st.button("Save Comments", key="save_comments"):
        last_session.comments = comments
        last_session.save()
        st.success("Comments saved successfully!")

if listener:
    try:
        command = ['C:\\Program Files\\Git\\bin\\bash.exe', './launch-listener.sh']
        if wheel:
            command.append('--wheel')
        if redis:
            command.append('--redis')
        process = subprocess.Popen(command, cwd='..', creationflags=subprocess.CREATE_NEW_CONSOLE)
        st.success("Launching listener in another window...")
        process.wait()  # Wait for the process to complete
        st.success("Listener window closed successfully!")
    except Exception as e:
        st.error(f"Error opening Git Bash terminal: {str(e)}")