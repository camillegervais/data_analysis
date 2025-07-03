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

def interpolate_data_at_distance(distance_series, data_series, target_distances):
    """
    Interpolate data values at specific target distances.
    
    Parameters:
    - distance_series: 1D numpy array of distances.
    - data_series: 1D numpy array of data points corresponding to the distances.
    - target_distances: 1D numpy array of distances at which to interpolate.
    
    Returns:
    - A numpy array of interpolated data values at the target distances.
    """
    if not (isinstance(distance_series, np.ndarray) and 
            isinstance(data_series, np.ndarray) and 
            isinstance(target_distances, np.ndarray)):
        raise ValueError("All inputs must be numpy arrays.")
    
    # Create interpolation function
    interpolated_values = np.interp(
        target_distances,
        distance_series,
        data_series,
        left=np.nan,   # Use NaN for values outside the range
        right=np.nan
    )
    
    return interpolated_values


def common_distance_serie(distance1, data1, distance2, data2, method="first_as_reference"):
    """
    Find common points between two distance series and interpolate data points.

    Parameters:
    - distance1: 1D numpy array of distances for the first series.
    - data1: 1D numpy array of data points corresponding to the first series.
    - distance2: 1D numpy array of distances for the second series.
    - data2: 1D numpy array of data points corresponding to the second series.
    - method: String specifying the method to use:
        - "first_as_reference": Use the first series distances as reference (default)
        - "union": Use the union of both distance series as reference
        - "intersection": Use only the exact common distances between both series

    Returns:
    - A tuple containing three arrays:
        - Common distances (numpy array)
        - Data values for first series at common distances (numpy array)
        - Data values for second series at common distances (numpy array)
    """
    if not (isinstance(distance1, np.ndarray) and isinstance(data1, np.ndarray) and
            isinstance(distance2, np.ndarray) and isinstance(data2, np.ndarray)):
        raise ValueError("All inputs must be numpy arrays.")
    
    # Ensure all arrays are 1D
    distance1 = distance1.flatten()
    data1 = data1.flatten()
    distance2 = distance2.flatten()
    data2 = data2.flatten()
    
    if method == "intersection":
        # Find exact intersections only
        common_distances = np.intersect1d(distance1, distance2)
        
        # Initialize arrays for data values
        data1_common = np.zeros(common_distances.shape)
        data2_common = np.zeros(common_distances.shape)
        
        for i, dist in enumerate(common_distances):
            idx1 = np.where(distance1 == dist)[0]
            idx2 = np.where(distance2 == dist)[0]
            
            if idx1.size > 0 and idx2.size > 0:
                data1_common[i] = data1[idx1[0]]
                data2_common[i] = data2[idx2[0]]
    
    elif method == "first_as_reference":
        # Use the first series distances as reference points
        common_distances = distance1
        
        # First series data is already aligned with common_distances
        data1_common = data1
        
        # Interpolate second series data at first series distances
        data2_common = interpolate_data_at_distance(distance2, data2, common_distances)
        
        # Filter out points where interpolation failed (NaN values)
        valid_indices = ~np.isnan(data2_common)
        common_distances = common_distances[valid_indices]
        data1_common = data1_common[valid_indices]
        data2_common = data2_common[valid_indices]
    
    elif method == "union":
        # Use the union of both distance series as reference
        common_distances = np.union1d(distance1, distance2)
        common_distances = np.sort(common_distances)  # Ensure distances are in order
        
        # Interpolate both series data at the union distances
        data1_common = interpolate_data_at_distance(distance1, data1, common_distances)
        data2_common = interpolate_data_at_distance(distance2, data2, common_distances)
        
        # Keep only points where at least one interpolation succeeded
        valid_indices = ~(np.isnan(data1_common) & np.isnan(data2_common))
        common_distances = common_distances[valid_indices]
        data1_common = data1_common[valid_indices]
        data2_common = data2_common[valid_indices]
        
        # Replace remaining NaN values with zeros or another placeholder
        data1_common = np.nan_to_num(data1_common, nan=0.0)
        data2_common = np.nan_to_num(data2_common, nan=0.0)
    
    else:
        raise ValueError(f"Unknown method: {method}. Choose from 'first_as_reference', 'union', or 'intersection'.")
    
    return common_distances, data1_common, data2_common