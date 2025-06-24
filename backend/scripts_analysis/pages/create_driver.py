"""
Script that uses the Streamlit library to create a driver
This script is used to create a driver in the database.
"""

import streamlit as st

import os
import django
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Driver

def create_driver():
    driver = Driver.objects.create(
        name=driver_name,
        age=driver_age
    )
    driver.save()
    pass

st.set_page_config(page_title="Driver Creation", page_icon=":guardsman:", layout="wide")

st.title("Create a Driver")
st.write("This is where you can create a driver in the database.")

driver_name = st.text_input("Driver Name")
driver_age = st.number_input("Driver Age", min_value=16, max_value=100)

st.button("Create Driver", on_click=create_driver)
