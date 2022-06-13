"""
    Utility functions to be shared by the time-series preprocessing required to feed the data into the synthesizers
"""
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from pickle import dump

# Method implemented here: https://github.com/jsyoon0823/TimeGAN/blob/master/data_loading.py
# Originally used in TimeGAN research
def real_data_loading(data: np.array, seq_len):
    """Load and preprocess real-world datasets.
    Args:
      - data_name: Numpy array with the values from a a Dataset
      - seq_len: sequence length

    Returns:
      - data: preprocessed data.
    """
    # Flip the data to make chronological data
    # ori_data = data[::-1]
    ori_data = data
    # Normalize the data
    scaler = MinMaxScaler().fit(ori_data)
    ori_data = scaler.transform(ori_data)
    # save the scaler
    dump(scaler, open('scaler.pkl', 'wb'))

    # Preprocess the dataset
    temp_data = []
    # Cut data by sequence length
    for i in range(0, len(ori_data) - seq_len):
        _x = ori_data[i:i + seq_len]
        temp_data.append(_x)

    # Mix the datasets (to make it similar to i.i.d)
    idx = np.random.permutation(len(temp_data))
    data = []
    for i in range(len(temp_data)):
        data.append(temp_data[idx[i]])
    return data
