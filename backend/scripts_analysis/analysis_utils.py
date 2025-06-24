import numpy as np
from sklearn.neighbors import LocalOutlierFactor

def rolling_average(data, window_size):
    """
    Calculate the rolling average of a 1D numpy array.
    
    Parameters:
    - data: 1D numpy array of data points.
    - window_size: Size of the rolling window.
    
    Returns:
    - A numpy array containing the rolling averages.
    """
    if not isinstance(data, np.ndarray):
        raise ValueError("Input data must be a numpy array.")
    
    if len(data) < window_size or window_size <= 0:
        raise ValueError("Window size must be positive and less than or equal to the length of the data.")
    
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def remove_outliers(data, n_neighbors=20):
    """
    Remove outliers from a 1D numpy array using Local Outlier Factor (LOF).

    Parameters:
    - data: 1D numpy array of data points.
    - n_neighbors: Number of neighbors to use for LOF calculation.

    Returns:
    - A numpy array with outliers removed.
    """
    if not isinstance(data, np.ndarray):
        raise ValueError("Input data must be a numpy array.")

    if len(data.shape) != 1:
        raise ValueError("Input data must be a 1D numpy array.")

    data = data.reshape(-1, 1)  # Reshape for LOF
    lof = LocalOutlierFactor(n_neighbors=n_neighbors)
    is_inlier = lof.fit_predict(data) == 1
    # Create a copy of the original data
    data_cleaned = data.copy()
    
    # For each outlier point, replace it with mean of surrounding values
    for i in range(len(data)):
        if not is_inlier[i]:
            # Define window boundaries
            window_size = 20
            start = max(0, i - window_size)
            end = min(len(data), i + window_size + 1)
            
            # Get only inlier values within the window
            window_values = data[start:end][is_inlier[start:end]]
            
            # If we have surrounding values, use their mean
            if len(window_values) > 0:
                data_cleaned[i] = np.mean(window_values)
            
    return data_cleaned.flatten(), data.size - np.sum(is_inlier)  # Return cleaned data and number of outliers removed