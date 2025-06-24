"""
Script that uses the Streamlit library to visualize session details and lap metrics
This script allows users to select a session and view its details, lap information, and metrics.
"""

import streamlit as st
import os
import django
import sys
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from simracing.models import Session, Lap
from scripts_analysis.utils import format_lap_time

def view_session():
    selected_session = st.selectbox(
        "Select Session",
        list(Session.objects.all()),
        format_func=lambda x: f"Session {x.id} - {x.track.name} ({x.date})"
    )
    st.write(f"### Session Details")
    left, right = st.columns(2)
    left.write(f"**Track**: {selected_session.track.name}")
    left.write(f"**Driver**: {selected_session.driver.name}")
    left.write(f"**Car**: {selected_session.car.name}")
    right.write(f"**Date**: {selected_session.date}")
    right.write(f"**Weather**: {selected_session.weather}")
    right.write(f"**Session Type**: {selected_session.session_type}")

    laps = Lap.objects.filter(session=selected_session)

    if laps.exists():
        container = st.container()

        st.write(f"### Lap Information")
        lap_times = []
        for lap in laps:
            left, middle, right = st.columns(3)
            left.write(f"**Lap ID**: {lap.id}")
            left.write(f"**Time**: {format_lap_time(lap.time)}")
            middle.write(f"**Fuel Used**: {lap.fuel} L")
            right.write(f"**Valid Lap**: {'Yes' if lap.valid_lap else 'No'}")
            if right.button("View Lap Plot", key=f"view_lap_plot_{lap.id}"):
                st.session_state.studied_lap_id = lap.id
                st.switch_page("pages/view_lap_plots.py")
                # Here you would call a function to display the lap plot, e.g., view_lap_plot(lap.id)
            st.write("---")
            lap_times.append(lap.time)

        mean_time = sum(lap_times) / len(lap_times)
        duration = sum(lap_times)
        best_time = min(lap_times)

        container.write(f"### Session Metrics")
        container.write(f"**Total Duration**: {format_lap_time(duration)}")
        container.write(f"**Mean Lap Time**: {format_lap_time(mean_time)}")
        container.write(f"**Best Lap Time**: {format_lap_time(best_time)}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(lap_times) + 1)),
            y=lap_times, name="Lap Times",
            mode='lines+markers'),
        )
        fig.update_layout(
            title="Lap Times",
            xaxis_title="Lap Number",
            yaxis_title="Time (seconds)",
        )

        container.plotly_chart(fig)
    else:
        st.write("No laps found for this session.")

st.set_page_config(page_title="Session Viewer", page_icon=":stopwatch:", layout="wide")

st.title("View Session Details")
st.write("Select a session to view its details, lap information, and metrics.")

view_session()