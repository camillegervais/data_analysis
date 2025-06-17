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
    
def median_value_session(session_data, key):
    """
    Calculate the median value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the median value.
    
    Returns:
        float: The median value of the specified key across all laps.
    """
    values = []
    for lap in session_data:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.median(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")
    
def l2_norm_session(session_data, key):
    """
    Calculate the L2 norm of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the L2 norm.
    
    Returns:
        float: The L2 norm of the specified key across all laps.
    """
    values = []
    for lap in session_data:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.linalg.norm(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def max_value_session(session_data, key):
    """
    Get the maximum value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to find the maximum value.
    
    Returns:
        float: The maximum value of the specified key across all laps.
    """
    values = []
    for lap in session_data:
        if key in lap:
            values.append(lap[key])
    if values:
        return max(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def min_value_session(session_data, key):
    """
    Get the minimum value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to find the minimum value.
    
    Returns:
        float: The minimum value of the specified key across all laps.
    """
    values = []
    for lap in session_data:
        if key in lap:
            values.append(lap[key])
    if values:
        return min(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def average_value_session(session_data, key):
    """
    Calculate the average value of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the average value.
    
    Returns:
        float: The average value of the specified key across all laps.
    """
    values = []
    for lap in session_data:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.mean(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")

def standard_deviation_session(session_data, key):
    """
    Calculate the standard deviation of a given key across all laps in a session.
    
    Args:
        session_data (list): List of dict for each lap in the session.
        key (str): The key for which to calculate the standard deviation.
    
    Returns:
        float: The standard deviation of the specified key across all laps.
    """
    values = []
    for lap in session_data:
        if key in lap:
            values.append(lap[key])
    if values:
        return np.std(values)
    else:
        raise KeyError(f"Key '{key}' not found in session data.")


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
        

