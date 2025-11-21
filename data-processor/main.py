import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime

from models_ml import * # Import the functions from other file


API_URL = "http://localhost:8080/api/data" # Spring Boot (or Java) API endpoint



def generate_synthetic_patient(): #Synthetic Patient Data Generator
    """
    Creates a single, realistic-looking patient entry.
    """
    complaints = ["Chest Pain", "Fever", "Broken Arm", "Headache", "Breathing Issues", "Stomach Pain"]
    triages = ["URGENT", "URGENT", "STANDARD", "STANDARD", "CRITICAL", "STANDARD"]
    
    idx = np.random.randint(0, len(complaints))
    
    patient = {
        "anonymousId": f"PT-{np.random.randint(1000, 9999)}",
        "complaint": complaints[idx],
        "triage": triages[idx], # Simple initial triage
        "status": "WAITING",
        "arrivalTime": datetime.now().isoformat()
    }
    return patient

# 2. API Client to Send Data
def send_data_to_api(patient_data):
    """
    Sends data to the Spring Boot API.
    NOTE: Your Java API must be running!
    """
    try:
        # We'll use the /api/patients endpoint you built in your Java example
        # (Assuming you add a POST handler to it)
        # For now, let's pretend we're sending new patient data.
        
        # A real endpoint might be: "http://localhost:8080/api/patients/check-in"
        # We'll use a placeholder URL and just print
        
        print(f"Sending data to API: {patient_data['anonymousId']}")
        
        # --- Uncomment this when your API is ready to receive POST data ---
        
        # headers = {'Content-Type': 'application/json'}
        # response = requests.post(API_URL, data=json.dumps(patient_data), headers=headers)
        
        # if response.status_code == 200 or response.status_code == 201:
        #     print("✅ Data sent successfully.")
        # else:
        #     print(f"API Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"🔴 FAILED TO CONNECT to API at {API_URL}.")
        print("   Please ensure the Java server is running.")
    except Exception as e:
        print(f"An error occurred: {e}")

# 3. Statistical Analysis Functions
def run_statistical_analysis(df):
    """
    Performs basic statistical analysis on the patient data.
    """
    if df.empty:
        return
        
    print("\n--- Statistical Analysis ---")
    avg_wait_time = df['waitTime'].mean()
    print(f"Average Wait Time: {avg_wait_time:.2f} mins")
    
    patients_by_triage = df.groupby('triage')['anonymousId'].count()
    print("Patients by Triage:")
    print(patients_by_triage)
    print("----------------------------\n")

# 4. Anomaly Detection (Simple Rule-Based)
def check_for_anomalies(df):
    """
    Looks for unusual patterns in the data.
    """
    if df.empty:
        return

    # Simple Anomaly: Wait time over 3 hours (180 mins)
    long_waits = df[df['waitTime'] > 180]
    if not long_waits.empty:
        print(f"🔴 ANOMALY DETECTED: {len(long_waits)} patients waiting > 3 hours!")
        
    # Simple Anomaly: Too many CRITICAL patients waiting
    critical_waiting = df[(df['triage'] == 'CRITICAL') & (df['status'] == 'WAITING')]
    if len(critical_waiting) > 3:
         print(f"🔴 ANOMALY DETECTED: {len(critical_waiting)} CRITICAL patients are waiting!")

# --- MAIN EXECUTION ---
def main_loop():
    """
    The main processing loop.
    """
    print("Starting Python Data Processing Pipeline...")
    
    # Let's create a fake database of patients for our simulation
    # We'll use the data from your Java server!
    try:
        print("Fetching initial patient data from Java API...")
        patients_response = requests.get("http://localhost:8080/api/patients")
        patient_list = patients_response.json()
        
        # Convert list of dicts to a Pandas DataFrame
        patient_df = pd.DataFrame(patient_list)
        print(f"✅ Loaded {len(patient_df)} patients from server.")
        
    except Exception as e:
        print(f"🔴 Error fetching from Java API: {e}")
        print("Starting with an empty patient list.")
        patient_df = pd.DataFrame(columns=["id", "anonymousId", "complaint", "triage", "status", "waitTime"])

    
    # --- Run Models ---
    wait_model = ml_models.train_wait_time_model(patient_df)
    forecast = ml_models.get_patient_flow_forecast()
    
    print(f"\nPatient Flow Forecast: {forecast}")
    
    
    # --- Run Analysis ---
    run_statistical_analysis(patient_df)
    check_for_anomalies(patient_df)
    
    
    # --- Simulate a New Patient Check-in ---
    print("\n--- Simulating New Patient Arrival ---")
    new_patient = generate_synthetic_patient()
    
    # Get a triage recommendation for the new patient
    recommendation = ml_models.get_triage_recommendation(new_patient)
    print(f"Triage Recommendation for {new_patient['complaint']}: {recommendation}")
    new_patient['triage'] = recommendation # Use the model's idea
    
    # Send new patient to the API
    send_data_to_api(new_patient)
    

if __name__ == "__main__":
    # This block means "run this code only when I execute main.py directly"
    main_loop()