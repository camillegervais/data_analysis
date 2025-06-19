import pandas as pd
import numpy as np
import os
import json

def load_data_session(session_id):
    """
    Load the data of the different laps of a session.
    args:
        session_id (int): The ID of the session to load.

    returns: 
        list of dictionaries: Each dictionary contains the data of a lap.
        list of pandas DataFrame: Each DataFrame contains the telemetry data of a lap.
    """

    telemetry_path = "./../telemetry_data"
    session_path = "./../session_data"
    session_dict = []
    session_df = []

    # Get list of all JSON files in telemetry_path
    json_files = [f for f in os.listdir(telemetry_path) if f.endswith('.json')]

    # Filter files for the specific session_id
    session_files = []
    for f in json_files:
        with open(os.path.join(telemetry_path, f), 'r') as file:
            data = json.load(file)
            if data.get('session') == session_id:  # assuming session_id is stored in the JSON
                session_files.append(f)

    for file in session_files:
        # Load JSON data
        with open(os.path.join(telemetry_path, file), 'r') as f:
            lap_data = json.load(f)
            session_dict.append(lap_data)

        # Load corresponding HDF5 file
        csv_file_path = os.path.join(telemetry_path, file.replace('.json', '.csv'))
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)
            session_df.append(df)
        else:
            print(f"CSV file for {file} not found.")
    
    # Create session info
    session_info = json.load(open(os.path.join(session_path, f'session_{session_id}_data.json'), 'r'))
    return session_info, session_dict, session_df

def l2_norm_lap(df, key):
    """
    Calculate the L2 norm of a given key in a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        key (str): The key for which to calculate the L2 norm.
    
    Returns:
        float: The L2 norm of the specified key.
    """
    if key in df.columns:
        return np.linalg.norm(df[key].values)
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")
    
def max_value_lap(df, key):
    """
    Get the maximum value of a given key in a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        key (str): The key for which to find the maximum value.
    
    Returns:
        float: The maximum value of the specified key.
    """
    if key in df.columns:
        return df[key].max()
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")
    
def min_value_lap(df, key):
    """
    Get the minimum value of a given key in a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        key (str): The key for which to find the minimum value.
    
    Returns:
        float: The minimum value of the specified key.
    """
    if key in df.columns:
        return df[key].min()
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")
    
def average_value_lap(df, key):
    """
    Calculate the average value of a given key in a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        key (str): The key for which to calculate the average value.
    
    Returns:
        float: The average value of the specified key.
    """
    if key in df.columns:
        return df[key].mean()
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")

def proportion_value_lap(df, key, value):
    if key in df.columns:
        return np.sum(np.array(df[key] == value))/np.array(df[key]).size
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")

def proportion_threshold_lap(df, key, value):
    if key in df.columns:
        return np.sum(np.array(df[key] > value))/np.array(df[key]).size
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")

def standard_deviation_lap(df, key):
    """
    Calculate the standard deviation of a given key in a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        key (str): The key for which to calculate the standard deviation.
    
    Returns:
        float: The standard deviation of the specified key.
    """
    if key in df.columns:
        return df[key].std()
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")
    
def median_value_lap(df, key):
    """
    Calculate the median value of a given key in a DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        key (str): The key for which to calculate the median value.
    
    Returns:
        float: The median value of the specified key.
    """
    if key in df.columns:
        return df[key].median()
    else:
        raise KeyError(f"Key '{key}' not found in DataFrame columns.")
    
def median_value_session(session_dict, key):
    """
    Calculate the median value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the median value.
    
    Returns:
        float: The median value of the specified key across all laps.
    """
    values = []
    for lap in session_dict:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.median(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")
    
def l2_norm_session(session_dict, key):
    """
    Calculate the L2 norm of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the L2 norm.
    
    Returns:
        float: The L2 norm of the specified key across all laps.
    """
    values = []
    for lap in session_dict:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.linalg.norm(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def max_value_session(session_dict, key):
    """
    Get the maximum value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to find the maximum value.
    
    Returns:
        float: The maximum value of the specified key across all laps.
    """
    values = []
    for lap in session_dict:
        if key in lap:
            values.append(lap[key])
    if values:
        return max(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def min_value_session(session_dict, key):
    """
    Get the minimum value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to find the minimum value.
    
    Returns:
        float: The minimum value of the specified key across all laps.
    """
    values = []
    for lap in session_dict:
        if key in lap:
            values.append(lap[key])
    if values:
        return min(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def average_value_session(session_dict, key):
    """
    Calculate the average value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the average value.
    
    Returns:
        float: The average value of the specified key across all laps.
    """
    values = []
    for lap in session_dict:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.mean(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")
    
def sum_value_session(session_dict, key):
    """
    Calculate the sum of the value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the sum.
    
    Returns:
        float: The sum of the specified key across all laps.
    """
    sum = 0
    for lap in session_dict:
        if key in lap:
            sum += lap[key]
    return sum

def standard_deviation_session(session_dict, key):
    """
    Calculate the standard deviation of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the standard deviation.
    
    Returns:
        float: The standard deviation of the specified key across all laps.
    """
    values = []
    for lap in session_dict:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.std(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def get_metrics_lap_data(dfs, key):
    v_mean = round(np.mean(np.array([average_value_lap(df, key) for df in dfs])), 2)
    v_max = round(np.amax(np.array([max_value_lap(df, key) for df in dfs])), 2)
    v_min = round(np.amin(np.array([min_value_lap(df, key) for df in dfs])), 2)
    v_std = round(np.std((np.hstack([df[key] for df in dfs]))), 2)
    return v_mean, v_max, v_min, v_std

def inertial_mapping(df):
    """
    Function to generate the speed and the position of the car throughout the lap, using the inertial mapping technique.
    Requires the DataFrame with telemetry data.
    """
    speed = df['speed'].values / 3.6  # Convert speed from km/h to m/s
    g_lat = df['g_force_0'].values * 9.81
    time = df['time'].values / 1000  # Convert time from ms to seconds

    # angle, x, y
    position = [[0, 0, 0]]
    delta_angle_list = []

    for i in range(1, len(speed)):
        if g_lat[i] != 0:
            dt = time[i] - time[i-1]
            delta_angle = (g_lat[i]/speed[i]**2) * (dt * speed[i])
            if abs(delta_angle) < np.pi:
                delta_angle_list.append(delta_angle)
            else:
                delta_angle_list.append(0)
                delta_angle = 0
        else:
            delta_angle = 0
            delta_angle_list.append(0)

        displacement = speed[i] * (time[i] - time[i-1])

        # filter huge displacement
        if abs(displacement) < 100:
            position.append([position[-1][0] + delta_angle, 
                             position[-1][1] + displacement * np.cos(position[-1][0] + delta_angle),
                             position[-1][2] + displacement * np.sin(position[-1][0] + delta_angle)])
            
    # Resolve the case where the final position is not the same as the initial position
    distance_vector = np.array([position[-1][1] - position[0][1], position[-1][2] - position[0][2]])
    for i in range(len(position)):
        position[i][1] -= distance_vector[0]*((i+1)/len(position))
        position[i][2] -= distance_vector[1]*((i+1)/len(position))

    return np.array(position), np.array(speed)

if __name__ == "__main__":
    pass
    # # Example usage
    # session_id = 29  # Replace with the actual session ID you want to load
    # session_data, telemetry_data = load_data_session(session_id)
    
    # print(f"Loaded {len(session_data)} laps for session {session_id}.")
    # for lap in session_data:
    #     print(lap)
    
    # print(f"Loaded {len(telemetry_data)} telemetry data files for session {session_id}.")
    # for df in telemetry_data:
    #     print(df.head())
        

