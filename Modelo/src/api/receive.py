import requests
import time
import json
from commands import commands
import time

class Receive():
    def __init__(self):
        self.API_URL = commands["API_URL_RECEIVE"]
        self.last_log_file = "last_log.json"
        
        self.last_data = self.load_last_data()

    def _fetch_new_data(self):
        response = requests.get(self.API_URL)
        if response.status_code == 200:
            data = response.json()
            return data['logs']
        else:
            print(f"Erro ao acessar a API: {response.status_code}")
            return None

    def load_last_data(self):
        try:
            with open(self.last_log_file, "r") as f:
                last_data = json.load(f)
                return last_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_last_data(self):
        with open(self.last_log_file, "w") as f:
            json.dump(self.last_data, f)

    def monitor_logs(self):
        while True:
            logs = self._fetch_new_data()
            
            if logs:
                if logs[-1] != self.last_data:
                    self.last_data = logs[-1]
                    self.save_last_data()
                    return logs[-1]
        
            time.sleep(2)

if __name__ == "__main__":
    receiver = Receive()
    receiver.monitor_logs()
