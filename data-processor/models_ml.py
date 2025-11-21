# main p
"""
This model trains ED waiting times and outputs the 
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


df = pd.read_csv(r"C:\Users\sorin.creanga\Desktop\Medcare\base-data\ER Wait Time Dataset.csv", index_col=0)

def train_wait_time_pred(df):
    """ This model trains and precits waiting times in ER room for incoming pacients.
    """

    

