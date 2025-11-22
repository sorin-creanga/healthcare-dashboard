import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

def train_wait_time_model(df):
    # 1. Basic Preprocessing
    le = LabelEncoder()
    # Convert text categories to numbers so the model can understand
    df['triage_code'] = le.fit_transform(df['triage']) 
    
    # 2. Define Features (X) and Target (Y)
    X = df[['triage_code']] # In real life, add more columns like time of day
    y = df['wait_time_minutes']
    
    # 3. Train Model
    model = RandomForestRegressor(n_estimators=10)
    model.fit(X, y)
    
    print("✅ Model trained successfully")
    return model

def get_triage_recommendation(patient_data):
    # Simple rule-based logic for the demo
    complaint = patient_data.get('complaint', '').lower()
    if 'chest' in complaint or 'breathing' in complaint:
        return 'CRITICAL'
    elif 'blood' in complaint or 'broken' in complaint:
        return 'URGENT'
    else:
        return 'STANDARD'