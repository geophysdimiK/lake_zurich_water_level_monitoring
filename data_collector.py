import requests 
import schedule
import time 

import pandas as pd 
from datetime import datetime

STATION = "mythenquai"
URL = f"https://tecdottir.metaodi.ch/measurements/{STATION}?sort=timestamp_cet%20desc&limit=1"

def fetch_and_save():
    response = requests.get(URL)
    
    if response.status_code == 200:
        
        result = response.json()['result'][0]['values'] #Extract the latest result set with the corresponding water level and the timestep
        timestamp = result['timestamp_cet']['value']
        level = result['water_level']['value']

        df = pd.DataFrame([[timestamp, level]], columns=["timestamp", "level"])
        df.to_csv("zuerichsee_history.csv", mode='a', index=False, header=False)
        print(f"[{datetime.now()}] Saved: {timestamp} - {level} m")
    else:
        print(f"Error: {response.status_code}")

# Fetch and save every 30 minutes
schedule.every(30).minutes.do(fetch_and_save)

# Continuous running of the script
while True:
    schedule.run_pending()
    time.sleep(1)
