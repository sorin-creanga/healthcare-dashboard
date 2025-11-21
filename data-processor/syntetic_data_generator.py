
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data(n_samples=5000): # artificial realistic ED data
 
    np.random.seed(42)
    
    # realistic data distributions
    health_levels = ['RESUSCITATION', 'EMERGENT', 'URGENT', 'SEMI_URGENT', 'NON_URGENT']
    health_probabilities = [0.05, 0.15, 0.30, 0.35, 0.15] 
    
    complaints = [
        'Chest Pain', 'Fever', 'Broken Arm', 'Headache', 'Breathing Issues',
        'Stomach Pain', 'Back Pain', 'Dizziness', 'Nausea', 'Laceration',
        'Allergic Reaction', 'Anxiety', 'Fracture', 'Burns', 'Syncope'
    ]
    
    dispositions = ['Admitted', 'Discharged', 'AMA', 'Transferred', 'Observation']
    disposition_probs = [0.30, 0.60, 0.05, 0.03, 0.02]
    
    
    data = {
        'patient_id': range(1, n_samples + 1),
        'anonymousId': [f'PT-{i:05d}' for i in range(1, n_samples + 1)],
        
        # arrival times with realistic patterns (busier in morning/evening)
        'arrival_time': [
            datetime.now() - timedelta(
                hours=np.random.exponential(scale=12),
                minutes=np.random.randint(0, 60)
            ) for _ in range(n_samples)
        ],
        
    
        'triage': np.random.choice(health_levels, n_samples, p=health_probabilities),
        
       
        'complaint': np.random.choice(complaints, n_samples),
        
        
        'wait_time_minutes': np.random.exponential(scale=45, size=n_samples),
        
        
        'door_to_doctor_minutes': np.random.exponential(scale=60, size=n_samples),
        
        
        'length_of_stay_minutes': np.random.exponential(scale=120, size=n_samples),
        
       
        'left_without_seen': np.random.binomial(1, 0.06, n_samples),
        
        
        'discharge_disposition': np.random.choice(
            dispositions, n_samples, p=disposition_probs
        ),
        
        
        'patient_age': np.random.gamma(shape=2, scale=25, size=n_samples).astype(int) + 5,
        
        
        'gender': np.random.choice(['M', 'F'], n_samples, p=[0.48, 0.52]),
    }
    
    df = pd.DataFrame(data)
    
   
    triage_map = {
        'RESUSCITATION': 1, 'EMERGENT': 2, 'URGENT': 3,
        'SEMI_URGENT': 4, 'NON_URGENT': 5
    }
    df['triage_numeric'] = df['triage'].map(triage_map)
    
    # Adjust LWBS based on triage (higher urgency = less likely to leave)
    lwbs_adjustment = df['triage_numeric'] / 5
    df['left_without_seen'] = (np.random.random(n_samples) > (1 - lwbs_adjustment * 0.08)).astype(int)
    
    # Correlation: longer waits increase LWBS risk
    long_wait_mask = df['wait_time_minutes'] > df['wait_time_minutes'].quantile(0.75)
    additional_lwbs = np.random.binomial(1, 0.15, sum(long_wait_mask))
    df.loc[long_wait_mask, 'left_without_seen'] = np.maximum(
        df.loc[long_wait_mask, 'left_without_seen'].values,
        additional_lwbs
    )
    
    # Add current status
    statuses = ['WAITING_FOR_TRIAGE', 'IN_TRIAGE', 'WAITING_FOR_DOCTOR', 
                'IN_CONSULTATION', 'UNDER_OBSERVATION', 'DISCHARGED']
    df['status'] = np.random.choice(statuses, n_samples)
    
    # Clean up
    df = df.drop('triage_numeric', axis=1)
    
    # Sort by arrival time
    df = df.sort_values('arrival_time').reset_index(drop=True)
    
    return df


def get_realtime_metrics(df):
    """
    Calculate current ED metrics from patient data
    
    Returns:
        dict: Current ED metrics
    """
    if df.empty:
        return {
            'total_patients': 0,
            'waiting_patients': 0,
            'in_treatment': 0,
            'average_wait_time': 0,
            'lwbs_rate': 0,
            'occupancy_rate': 0,
            'critical_patients': 0,
            'saturation_level': 'GREEN'
        }
    
    waiting = len(df[df['status'].isin(['WAITING_FOR_TRIAGE', 'WAITING_FOR_DOCTOR'])])
    in_treatment = len(df[df['status'].isin(['IN_TRIAGE', 'IN_CONSULTATION', 'UNDER_OBSERVATION'])])
    
    avg_wait = df['wait_time_minutes'].mean() if 'wait_time_minutes' in df.columns else 0
    lwbs_count = df['left_without_seen'].sum() if 'left_without_seen' in df.columns else 0
    lwbs_rate = (lwbs_count / len(df) * 100) if len(df) > 0 else 0
    
    critical = len(df[df['triage'] == 'CRITICAL']) if 'triage' in df.columns else 0
    
    # Saturation level logic
    occupancy = in_treatment / max(25, len(df))  # Assume ED capacity ~25
    if len(df) > 20 or occupancy > 0.8:
        saturation = 'RED'
    elif len(df) > 12 or occupancy > 0.5:
        saturation = 'YELLOW'
    else:
        saturation = 'GREEN'
    
    return {
        'total_patients': len(df),
        'waiting_patients': waiting,
        'in_treatment': in_treatment,
        'average_wait_time': round(avg_wait, 2),
        'lwbs_rate': round(lwbs_rate, 2),
        'occupancy_rate': round(occupancy * 100, 2),
        'critical_patients': critical,
        'saturation_level': saturation
    }


def detect_anomalies(df):
    """
    Detects unusual patterns in ED data
    
    Returns:
        list: List of anomaly alerts
    """
    alerts = []
    
    if df.empty:
        return alerts
    
    # Check for excessive wait times
    if 'wait_time_minutes' in df.columns:
        long_waits = len(df[df['wait_time_minutes'] > 180])
        if long_waits > 3:
            alerts.append({
                'severity': 'HIGH',
                'message': f'{long_waits} patients waiting > 3 hours'
            })
    
    # Check for high LWBS rate
    if 'left_without_seen' in df.columns:
        lwbs_rate = (df['left_without_seen'].sum() / len(df) * 100) if len(df) > 0 else 0
        if lwbs_rate > 8:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f'LWBS rate elevated: {lwbs_rate:.1f}%'
            })
    
    # Check for too many critical patients
    critical_count = len(df[df['triage'] == 'CRITICAL']) if 'triage' in df.columns else 0
    if critical_count > 5:
        alerts.append({
            'severity': 'HIGH',
            'message': f'{critical_count} CRITICAL patients currently waiting'
        })
    
    # Check for ED overcrowding
    if len(df) > 20:
        alerts.append({
            'severity': 'MEDIUM',
            'message': f'ED approaching capacity: {len(df)} patients'
        })
    
    return alerts


if __name__ == "__main__":
    # Example usage
    print("Generating 500 sample patients...")
    df = generate_synthetic_data(500)
    
    print(f"\nGenerated {len(df)} patient records")
    print(f"\nData Summary:")
    print(df[['patient_id', 'triage', 'complaint', 'wait_time_minutes', 'status']].head(10))
    
    print(f"\nCurrent Metrics:")
    metrics = get_realtime_metrics(df)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print(f"\nAnomalies Detected:")
    anomalies = detect_anomalies(df)
    for alert in anomalies:
        print(f"  [{alert['severity']}] {alert['message']}")