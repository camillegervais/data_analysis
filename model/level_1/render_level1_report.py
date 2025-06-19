from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from utils import format_lap_time
import matplotlib.pyplot as plt

from backend.scripts_analysis.inertial_mapping import inertial_mapping

import numpy as np

from model.level_1.level_1_analysis import *
import os

def create_report(session_id):
    template_path = "./template/structure_niveau_1.tex"
    report_path = f"./report/session_{session_id}/level_1_report_{session_id}.tex"

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    session_info, dicts, dfs = load_data_session(session_id)

    # Replace placeholders with actual data (to be implemented later)
    report_content = template_content.replace("[Nom du circuit]", session_info['track'])
    report_content = report_content.replace("[Date]", session_info['date'])
    report_content = report_content.replace("[Essais Libres / Qualification / Course]", session_info['session_type'])
    report_content = report_content.replace("[Identifiant voiture]", session_info['car'])
    report_content = report_content.replace("[Nom pilote]", session_info['driver'])
    report_content = report_content.replace("[Nb Tour]", str(len(dicts)))
    report_content = report_content.replace("[Durée]", format_lap_time(sum_value_session(dicts, 'time')))
    report_content = report_content.replace("[XX °C / XX °C]", f"{prepare_float(average_value_session(dicts,'air_temp'))} °C / {prepare_float(average_value_session(dicts, 'road_temp'))} °C")

    report_content = report_content.replace("[Tmean]", format_lap_time(average_value_session(dicts, 'time')))
    report_content = report_content.replace("[Tmin]", format_lap_time(min_value_session(dicts, 'time')))
    report_content = report_content.replace("[Tmax]", format_lap_time(max_value_session(dicts, 'time')))
    report_content = report_content.replace("[Tstd]", format_lap_time(standard_deviation_session(dicts, 'time')))

    v_mean, v_max, v_min, v_std = get_metrics_lap_data(dfs, 'speed')

    g_mean, g_max, g_min, g_std = get_metrics_lap_data(dfs, 'g_force_2') # check the index, not sure if it's lateral acceleration

    report_content = report_content.replace("[Vmean\_session]", prepare_float(v_mean) + " km/h")
    report_content = report_content.replace("[Vmin\_session]", prepare_float(v_min) + " km/h")
    report_content = report_content.replace("[Vmax\_session]", prepare_float(v_max) + " km/h")
    report_content = report_content.replace("[Vstd\_session]", prepare_float(v_std) + " km/h")

    g = 9.81

    report_content = report_content.replace("[Gmean]", prepare_float(g_mean/g) + " G")
    report_content = report_content.replace("[Gmin]", prepare_float(g_min/g) + " G")
    report_content = report_content.replace("[Gmax]", prepare_float(g_max/g) + " G")
    report_content = report_content.replace("[Gstd]", prepare_float(g_std/g) + " G")

    # Fill the table with all the data from a lap

    final_str_tab_1 = ""
    final_str_tab_2 = ""
    lap_counter = 0

    for df in dfs:
        lap_counter += 1
        # print(f"Add the value of lap {lap_counter}")
        final_str_tab_1 += f"{lap_counter} & {format_lap_time(max_value_lap(df, 'time'))} & {prepare_float(max_value_lap(df, 'speed'))} km/h & {prepare_float(g_max)} G & {prepare_float(proportion_value_lap(df, 'throttle', 1.0))}\% \\\ \n"
        final_str_tab_2 += f"{lap_counter} & {prepare_float(proportion_threshold_lap(df, 'brake', 0))}\% & {prepare_float(l2_norm_lap(df, 'steering_angle'))}° & {prepare_float(max_value_lap(df, 'rpm'))} rpm & {prepare_float(max_value_lap(df, 'fuel') - min_value_lap(df, 'fuel'))}L \\\ \n"


    report_content = report_content.replace("[Lap Data]", final_str_tab_1)
    report_content = report_content.replace("[Lap Data 2]", final_str_tab_2)

    position, speed, beacons_position = inertial_mapping(dicts[0]['id'])
    plt.scatter(position[:, 1], position[:, 2], s=0.5, c=speed[:position.shape[0]]*3.6, cmap='viridis')  # Color by speed
    plt.scatter(beacons_position[:, 1], beacons_position[:, 2], c='red', s=10, label='Beacons')  # Plot beacons
    plt.colorbar(label='Speed (km/h)')  # Add a colorbar to show speed scale
    plt.axis('equal')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.imsave(os.path.dirname(report_path) + 'inertial_mapping.png')

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_content)

    print(f"Report generated at {report_path}")

def prepare_float(value):
    return str(round(value, 2))

if __name__ == "__main__":
    create_report(31)
    create_report(32)