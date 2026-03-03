# -*- coding: utf-8 -*-
import numpy as np
import os

data_dir = 'data/processed/'
features_path = os.path.join(data_dir, 'node_features.npy')
csv_features_path = os.path.join(data_dir, 'node_features.csv')

print('Checking for node_features.npy:', features_path)
if os.path.exists(features_path):
    try:
        features = np.load(features_path)
        print('Numpy features loaded successfully, shape:', features.shape)
    except Exception as e:
        print('Error loading numpy features:', e)
else:
    print('Numpy features file not found')

print('Checking for node_features.csv:', csv_features_path)
if os.path.exists(csv_features_path):
    import pandas as pd
    try:
        df = pd.read_csv(csv_features_path)
        print('CSV features loaded successfully, shape:', df.shape)
        print('Columns:', df.columns.tolist())
        # Convert to numpy array
        features_array = df.values
        print('Converted to numpy array, shape:', features_array.shape)
        # Save as numpy file
        np.save(features_path, features_array)
        print('Saved as numpy file')
    except Exception as e:
        print('Error processing CSV features:', e)
else:
    print('CSV features file not found')