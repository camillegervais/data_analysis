from scripts_analysis.inertial_mapping import inertial_mapping, render_plot
from scripts_analysis.database_explore import explore_database
from scripts_analysis.traction_circle import traction_circle

import sys

if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from simracing.models import Lap

    # Example usage
    if len(sys.argv) > 1:
        if sys.argv[1] == 'inertial_mapping':
            if len(sys.argv) > 2:
                lap_id = int(sys.argv[2])
            else:
                lap_id = 119  # Replace with the actual lap ID you want to process
            position, speed = inertial_mapping(lap_id)
            render_plot(position, speed)
        elif sys.argv[1] == 'explore_database':
            if len(sys.argv) > 2:
                object_name = sys.argv[2]
                explore_database(object_name)
            else:
                print("Enter the name of the object you want to explore")
        elif sys.argv[1] == 'traction_circle':
            if len(sys.argv) > 2:
                lap_id = int(sys.argv[2])
            else:
                lap_id = 119
            traction_circle(lap_id)
                
    else:
        print("Please give the name of the script you want to execute")
    