import numpy as np

def calculate_rms(data1, data2):
    if len(data1) != len(data2):
        raise ValueError("Data sets must have the same length.")
    
    squared_diffs = [(d1 - d2)**2 for d1, d2 in zip(data1, data2)]
    mean_squared_diff = sum(squared_diffs) / len(data1)
    rms = np.sqrt(mean_squared_diff)
    return rms