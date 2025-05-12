import requests
import time
from commands import commands
import sqlite3

class Send:
    def __init__(self):
        self.API_URL = commands["API_URL_SEND"]

    def send_log_to_api(self, log, user_id):
        try:
            response = requests.post(self.API_URL, json={
                "log": log,
                "user_id": user_id
            })

        except Exception as e:
            print(f"Erro ao conectar com a API: {str(e)}")


if __name__ == "__main__":
    send = Send()

    log_data = "Seu log aqui"
    send.send_log_to_api(log_data)