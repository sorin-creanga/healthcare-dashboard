import requests
import time
import pandas as pd
# Import the function directly from your generator file
from syntetic_data_generator import generate_synthetic_data

API_URL = "http://localhost:8080/api/patients"

def push_data():
    print("--- Generating Synthetic Data ---")
    # Generate 10 new patients using your existing generator
    df = generate_synthetic_data(n_samples=10)
    
    print(f"Generated {len(df)} patients. Sending to API...")

    for index, row in df.iterrows():
        
        # Map the dataframe columns to the Java API parameters
        params = {
            'chiefComplaint': row['complaint'],
            'triageLevel': row['triage'],
            'waitTime': int(row['wait_time_minutes'])  # <--- ADD THIS LINE
        }
        
        try:
            response = requests.post(API_URL, params=params)
            if response.status_code == 200:
                print(f"✅ Sent: {row['complaint']} ({row['triage']})")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Sleep briefly so we can see the updates happening
        time.sleep(1)

if __name__ == "__main__":
    push_data()