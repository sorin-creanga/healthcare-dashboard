# main p
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

def train_wait_time_pred(df):
    """ This model trains and precits waiting times in ER room for incoming pacients.
    """

    print("Predicted waiting time")

train_wait_time_pred(1)