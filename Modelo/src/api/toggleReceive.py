import requests
import time
import json
#from commands import commands
import time

class ToggleReceive():
    def __init__(self):
        self.API_URL = "http://localhost:8000/logs/toggle"

    def _fetch_new_data(self):
        response = requests.get(self.API_URL)
        if response.status_code == 200:
            data = response.json()
            return data['logs']
        else:
            print(f"Erro ao acessar a API: {response.status_code}")
            return None

    def monitor_logs(self):
        return self._fetch_new_data()[-1]

if __name__ == "__main__":
    receiver = ToggleReceive()
    receiver.monitor_logs()
