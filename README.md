## Using the `scripts_launcher.py` Script

The `scripts_launcher.py` script allows you to execute various data analysis tasks from the terminal. Below are the available commands and their usage:

### General Syntax
```bash
python backend/scripts_launcher.py <command> [arguments]
```

### Commands and Arguments

1. **`inertial_mapping`**
   - Description: Processes a lap and renders a plot of position, speed, and beacons.
   - Usage:
     ```bash
     python backend/scripts_launcher.py inertial_mapping [lap_id]
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py inertial_mapping 119
     ```

2. **`explore_database`**
   - Description: Explores the database for a specific object.
   - Usage:
     ```bash
     python backend/scripts_launcher.py explore_database <object_name>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py explore_database Track
     ```

3. **`traction_circle`**
   - Description: Generates a traction circle plot for a specific lap and beacon.
   - Usage:
     ```bash
     python backend/scripts_launcher.py traction_circle <lap_id> <beacon>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py traction_circle 119 start
     ```

4. **`speed_plot`**
   - Description: Plots the speed for one or more laps.
   - Usage:
     ```bash
     python backend/scripts_launcher.py speed_plot <lap_ids>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py speed_plot 119,120
     ```

5. **`beacons`**
   - Description: Sets beacons for a specific track.
   - Usage:
     ```bash
     python backend/scripts_launcher.py beacons <track_id>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py beacons 1
     ```

6. **`debug`**
   - Description: Executes debugging tasks, such as modifying the database.
   - Usage:
     ```bash
     python backend/scripts_launcher.py debug
     ```

7. **`export_csv`**
   - Description: Exports the data of a specific lap to a CSV file.
   - Usage:
     ```bash
     python backend/scripts_launcher.py export_csv <lap_id>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py export_csv 119
     ```

8. **`export_json`**
   - Description: Exports the data of a specific lap to a JSON format and prints it to the terminal.
   - Usage:
     ```bash
     python backend/scripts_launcher.py export_json <lap_id>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py export_json 119
     ```

9. **`export_lap`**
   - Description: Exports the data of a specific lap to both JSON and CSV files.
   - Usage:
     ```bash
     python backend/scripts_launcher.py export_lap <lap_id>
     ```
   - Example:
     ```bash
     python backend/scripts_launcher.py export_lap 119
     ```

### Notes
- Replace `<command>` with the desired command.
- Replace `[arguments]` with the appropriate arguments for the command.
- Ensure the Django environment is properly set up before running the script.

## General architecture of the folder

### backend

In this folder is stored all the script using the database of django and the h5 files that are referenced in the database sqlite.

You can find all the classic django interface in simracing, backend.

In scripts_analysis you can find python scripts launched by scripts_launcher.py that allow you to visualize the datas stored in the database.

In telemetry_data are stored te h5 files of all the laps recorded. They are ignored by git.

### frontend

We use the React frontend interface for the final rendering of the app. No analysis is done in those scripts, only rendering. This interface is used to record laps with session associated, this allows us to put a context on the raw data of a lap.

### cdc

In this folder are the documents that structure the project.

### model

The main project is to make something out of the data and it is in this folder that the magic happens. Data stored in the backend folder are analyzed through this model and rendered with the frontend scripts.

## How to launch the website interface?

### frontend

Use  ```bash
     source launch_front.sh
    ``` 
in the data_analysis folder. You should be abe to visit the website but no data are available, for that we need the backend.

### backend

Use  ```bash
     source launch_back.sh
     ``` in the data_analysis folder.

### redis

In ubuntu you can type ```bash
     source launch_redis.sh
     ```. This is necessary to have live feedback of the data gathered by the listener. The installation must be done on an Ubuntu machine (use WSL if on Windows). The files in this git repo are not enough to make this work.

### listener

The listener is the script gathering data from the game and uploading them in the database. It is necessary when launching a new session and doing laps on the game.

To launch it, as usual, use :```bash
     source launch_listener.sh
     ``` in the data_analysis folder.

## Gather data from backend to model

### Export the data from backend

Use ```bash
     python scripts_launcher.py export_lap <lap_id>
     ``` in the backend folder. This will create the csv file and the json file needed by the model.

### Move these data to model

In the model folder, use ```bash
     ./get_data.sh
     ``` to copy the data in the correct folder in order for the model to analyze it.


