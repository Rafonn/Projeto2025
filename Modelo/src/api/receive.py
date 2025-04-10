import requests
import time
import json
from commands import commands

class Receive():
    def __init__(self):
        self.API_URL = commands["API_URL_RECEIVE"]
        self.last_log_file = "last_log.json"
        self.last_data = self.load_last_data()

    def _fetch_new_data(self):
        try:
            response = requests.get(self.API_URL)
            if response.status_code == 200:
                data = response.json()
                return data['logs']
            else:
                print(f"Erro ao acessar a API: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro na requisição: {e}")
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

    def monitor_logs(self, restart_flag=None, timeout=1.5):
        start_time = time.time()

        while True:
            # ⚠️ Interrompe se houve mudança de estado (restart_flag)
            if restart_flag and restart_flag.is_set():
                return None
            
            logs = self._fetch_new_data()
            if logs:
                if logs[-1] != self.last_data:
                    self.last_data = logs[-1]
                    self.save_last_data()
                    return logs[-1]

            if time.time() - start_time > timeout:
                return None

            time.sleep(0.2)  # mais responsivo
