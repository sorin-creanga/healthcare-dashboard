**Real-Time Emergency Department (ED) Analytics Platform**

**Project Overview**

This project simulates a Hospital Emergency Department dashboard. It uses a microservices-inspired architecture where Python generates synthetic patient data, and a Java backend processes this data to enforce hospital protocols (like triage rules) and visualizes the status in real-time.

**Why is this project needed?**

Safe Testing: Provides a risk-free environment to test critical algorithms, such as wait-time caps for urgent patients, before deploying them to real hospitals.




**How to Run**

Prerequisites

Java JDK (Version 8+)

Python 3 (with pip)

1. Install Python Dependencies

Open a terminal in the data-processor folder:

pip install -r requirements.txt


2. Start the Backend Server

Open a terminal in the backend folder:

javac -encoding UTF-8 QuickHealthcareAPI.java
java QuickHealthcareAPI


3. Launch the Dashboard

Open your browser to http://localhost:8080. The page will auto-refresh every 30 seconds.

4. Start the Data Feed

Open a new terminal window and run:

python push_to_api.py


Tech Stack

Java: com.sun.net.httpserver for lightweight HTTP handling.

Python: Pandas and Numpy for statistical data generation.

HTML/CSS: Server-Side Rendered UI with Meta-Refresh.

REST API: HTTP POST communication between the Python data layer and Java backend.
