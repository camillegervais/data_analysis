"""
Script that uses the Streamlit library to create a car
This script is used to create a car in the database.
"""

import streamlit as st

import os
import django
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Car

def create_car():
    car = Car.objects.create(
        name=car_name,
        model=car_model,
        manufacturer=car_manufacturer,
        year=car_year,
        weight=car_weight,
        power=car_power,
        torque=car_torque,
        top_speed=car_top_speed
    )
    car.save()
    pass

st.set_page_config(page_title="Car Creation", page_icon=":car:", layout="wide")

st.title("Create a Car")
st.write("This is where you can create a car in the database.")

car_name = st.text_input("Car Name")
car_model = st.text_input("Car Model")
car_manufacturer = st.text_input("Car Manufacturer")
car_year = st.number_input("Year of Manufacture", min_value=1900, max_value=2025)
car_weight = st.number_input("Car Weight (kg)", min_value=500, max_value=5000)
car_power = st.number_input("Car Power (HP)", min_value=50, max_value=2000)
car_torque = st.number_input("Car Torque (Nm)", min_value=50, max_value=2000)
car_top_speed = st.number_input("Car Top Speed (km/h)", min_value=50, max_value=500)

st.button("Create Car", on_click=create_car)
