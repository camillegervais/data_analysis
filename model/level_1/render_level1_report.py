from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from utils import format_lap_time
import matplotlib.pyplot as plt

import numpy as np

from level_1_analysis import *
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

    # Render an interial mapping of the fastest lap
    position, speed = inertial_mapping(dfs[np.argmin([dict['time'] for dict in dicts])])
    plt.scatter(position[:, 1], position[:, 2], s=0.5, c=speed[:position.shape[0]]*3.6, cmap='viridis')  # Color by speed
    plt.colorbar(label='Speed (km/h)')  # Add a colorbar to show speed scale
    plt.axis('equal')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.savefig(os.path.dirname(report_path) + '/inertial_mapping.png')
    plt.close()

    # Render the plot of the time through the session
    times = [dict['time'] for dict in dicts]
    plt.plot(range(1, len(times) + 1), times, marker='o')
    plt.title('Time per Lap')
    plt.xlabel('Lap Number')
    plt.ylabel('Lap Time (s)')
    plt.grid()
    plt.savefig(os.path.dirname(report_path) + '/lap_times.png')
    plt.close()

    index = np.argmin([dict['time'] for dict in dicts])
    plt.scatter(dfs[index]['slip_angle_0'], dfs[index]['g_force_0'], c='blue')
    plt.scatter(dfs[index]['slip_angle_1'], dfs[index]['g_force_0'], c='red')
    plt.scatter(dfs[index]['slip_angle_2'], dfs[index]['g_force_0'], c='green')
    plt.scatter(dfs[index]['slip_angle_3'], dfs[index]['g_force_0'], c='orange')
    plt.title('Slip Angle vs Lateral G-Force')
    plt.ylabel('Lateral G-Force (m/s²)')
    plt.xlabel('Slip Angle (degrees)')
    plt.grid()
    plt.savefig(os.path.dirname(report_path) + '/slip_angle_vs_lateral_g_force.png')
    plt.close()

    # Render the g-g plot for the fastest lap
    plt.scatter(dfs[index]['g_force_0'], dfs[index]['g_force_1'], c='blue')
    plt.title('Lateral vs Longitudinal G-Force')
    plt.xlabel('Lateral G-Force (m/s²)')
    plt.ylabel('Longitudinal G-Force (m/s²)')
    plt.grid()
    plt.savefig(os.path.dirname(report_path) + '/g_g_plot.png')
    plt.close()

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_content)

    print(f"Report generated at {report_path}")

def prepare_float(value):
    return str(round(value, 2))

if __name__ == "__main__":
    create_report(31)
    create_report(32)