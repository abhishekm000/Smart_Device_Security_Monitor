import threading
import time
import pandas as pd
import random
import os
import requests
from ..config import Config

class SimulationService:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.speed = 1.0 # seconds
        self.dataset = None
        self.current_index = 0

    def load_dataset(self):
        if self.dataset is None:
            sample_path = os.path.join(Config.DATA_DIR, 'sample', 'ciciot2023_sample.csv')
            try:
                self.dataset = pd.read_csv(sample_path)
                print(f"Simulation dataset loaded with {len(self.dataset)} rows.")
            except Exception as e:
                print(f"Error loading simulation dataset: {e}")
                return False
        return True

    def start(self, speed=1.0):
        if self.is_running:
            return False, "Simulation already running"
            
        if not self.load_dataset():
            return False, "Failed to load dataset"
            
        self.speed = speed
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        return True, "Simulation started"

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        return True, "Simulation stopped"

    def get_status(self):
        return {
            "is_running": self.is_running,
            "speed": self.speed,
            "current_index": self.current_index,
            "total_records": len(self.dataset) if self.dataset is not None else 0
        }

    def _run_loop(self):
        # We need an app context if we interact with the DB directly, 
        # or we can send requests to our own API
        # Sending requests is cleaner and perfectly matches the "SAME prediction pipeline"
        
        while self.is_running:
            if self.current_index >= len(self.dataset):
                self.current_index = 0 # loop back
                
            row = self.dataset.iloc[self.current_index].to_dict()
            
            # Prepare payload (drop label if exists, though ML service ignores it)
            if 'label' in row:
                del row['label']
                
            row['device_id'] = 'DEV-001'
            row['source_ip'] = f"192.168.1.{random.randint(10, 50)}"
            row['destination_ip'] = f"10.0.0.{random.randint(1, 10)}"
            
            try:
                # Send to our own API
                requests.post('http://127.0.0.1:5000/api/predict', json=row)
            except Exception as e:
                print(f"Simulation request failed: {e}")
                
            self.current_index += 1
            time.sleep(self.speed)

simulation_service = SimulationService()
