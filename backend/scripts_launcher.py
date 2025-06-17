from scripts_analysis.inertial_mapping import inertial_mapping, render_plot
from scripts_analysis.database_explore import explore_database, exportCSVLap, exportJsonLap, export_lap_data, export_session_data
from scripts_analysis.lap_plot import traction_circle, speed_plot, set_lap_beacons

import sys

from simracing.models import Track, Driver, Session, Car

def debug():
    """ Function to apply modifications to the database"""

    # correctif de l'attribution des temps de secteurs
    
    # assigner un exemples de beacons aux deux circuits dans la base de données
    track = Track.objects.get(name='SPA')
    driver = Driver.objects.get(name="Camille")
    car = Car.objects.get(name="McLaren 720S GT3")
    session = Session.objects.create(driver=driver, track=track, car=car, date='2023-10-01', weather='Sunny', session_type='Practice')
    session.save()

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
            position, speed, beacons = inertial_mapping(lap_id)
            render_plot(position, speed, beacons)
        elif sys.argv[1] == 'explore_database':
            if len(sys.argv) > 2:
                object_name = sys.argv[2]
                explore_database(object_name)
            else:
                print("Enter the name of the object you want to explore")
        elif sys.argv[1] == 'traction_circle':
            if len(sys.argv) > 3:
                lap_id = int(sys.argv[2])
                beacons = sys.argv[3]
            else:
                lap_id = 119
                beacons = 'start'
            traction_circle(lap_id, beacons)
        elif sys.argv[1] == 'speed_plot':
            if len(sys.argv) > 2:
                lap_id = [int(id) for id in sys.argv[2].split(',')]
            else:
                lap_id = [119]
            speed_plot(lap_id)
        elif sys.argv[1] == 'beacons':
            if len(sys.argv) > 2:
                track_id = int(sys.argv[2])
                beacons = {
                    'start': 0,
                    'T1': 450,
                    'T2': 650,
                } # This set of beacons has to be modified for every modification.
                set_lap_beacons(track_id, beacons)
            else:
                print("Enter the track ID and the beacons")
        elif sys.argv[1] == 'export_csv':
            if len(sys.argv) > 2:
                lap_id = int(sys.argv[2])
                lap = Lap.objects.get(id=lap_id)
                exportCSVLap(lap)
            else:
                print("Enter the lap ID you want to export")
        elif sys.argv[1] == 'export_json':
            if len(sys.argv) > 2:
                lap_id = int(sys.argv[2])
                lap = Lap.objects.get(id=lap_id)
                print(exportJsonLap(lap))
            else:
                print("Enter the lap ID you want to export")
        elif sys.argv[1] == 'export_lap':
            if len(sys.argv) > 2:
                lap_id = int(sys.argv[2])
                lap = Lap.objects.get(id=lap_id)
                json_path, csv_path = export_lap_data(lap)
                print(f"Lap data exported to {json_path} and {csv_path}")
            else:
                print("Enter the lap ID you want to export")
        elif sys.argv[1] == 'export_session':
            if len(sys.argv) > 2:
                session_id = int(sys.argv[2])
                export_session_data(session_id)
            else:
                print("Enter the session ID you want to export")
        elif sys.argv[1] == 'debug':
            debug()
        else:
            print(f"Unknown script: {sys.argv[1]}")
            print("Available scripts: inertial_mapping, explore_database, traction_circle, speed_plot, beacons, export_csv, export_json, export_lap, debug")
                
    else:
        print("Please give the name of the script you want to execute")
    