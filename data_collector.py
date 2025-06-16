import requests 
import schedule
import time 
import os

import pandas as pd 
from datetime import datetime

STATION = "mythenquai"
URL = f"https://tecdottir.metaodi.ch/measurements/{STATION}?sort=timestamp_cet%20desc&limit=1"

if not os.path.exists("zuerichsee_history.csv"):
    response = requests.get(URL)
    result = response.json()['result'][0]['values']
    timestamp = result['timestamp_cet']['value']
    level = result['water_level']['value']

    with open("zuerichsee_history.csv", "w") as f:
        f.write(f"{timestamp},{level}\n")
    

def fetch_and_save():
    response = requests.get(URL)
    
    if response.status_code == 200:
        
        result = response.json()['result'][0]['values'] #Extract the latest result set with the corresponding water level and the timestep
        timestamp = result['timestamp_cet']['value']
        level = result['water_level']['value']

        df = pd.DataFrame([[timestamp, level]], columns=["timestamp", "level"])
        df.to_csv("zuerichsee_history.csv", index=False, header=False)
        print(f"[{datetime.now()}] Saved: {timestamp} - {level} m")
    else:
        print(f"Error: {response.status_code}")

# Fetch and save every 3 minutes
schedule.every(3).minutes.do(fetch_and_save)

# Continuous running of the script
while True:
    schedule.run_pending()
    time.sleep(1)
