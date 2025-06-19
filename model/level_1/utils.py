def format_lap_time(lap_time):
    """
    Format the lap time from milliseconds to mm:ss,sss format.
    """
    lap_time = int(lap_time)  # Ensure lap_time is an integer
    seconds = lap_time // 1000
    milliseconds = lap_time % 1000
    minutes = seconds // 60
    return f"{minutes:02}:{seconds % 60:02},{milliseconds:03}"

def format_temperature(temperature):
    """
    Format the temperature in Celsius
    """
    temperature = float(temperature)  # Ensure temperature is a float
    return str(round(temperature, 2)) + "°C"