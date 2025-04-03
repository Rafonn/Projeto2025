import openai
import os
import json
import tiktoken
import time
import threading

from proData import ReadData
from api.send import Send
from api.receive import Receive
from api.toggleReceive import ToggleReceive
from data.status import OPCUAClient
from data.node_id_map import MachineMap
from maps.machines_ids import machines
from commands import commands

class ChatAndritz:
    def __init__(self, api_key, base_folder):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.base_folder = base_folder
        self.history = [{"role": "system", "content": commands["initial"]}]
        self.send_api = Send()
        self.receive_api = Receive()
        self.receive_toggle = ToggleReceive()

        self.verify_state = self._verify_input()
        self.restart_flag = threading.Event()

        self.monitor_thread = threading.Thread(target=self._monitor_input, daemon=True)
        self.monitor_thread.start()
    

    def _tokens_count(self, messages, model="gpt-3.5-turbo"):
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = sum(len(encoding.encode(m["content"])) for m in messages)
        return num_tokens
    
    def _monitor_input(self):
        while True:
            current_state = self._verify_input()
            if current_state != self.verify_state:
                self.verify_state = current_state
                self.restart_flag.set()
            time.sleep(0.1)

    def _check_restart(self):
        if self.restart_flag.is_set():
            self._log_and_print("⚠️ Mudança detectada! Reiniciando verificações...")
            return True
        return False



    def _log_and_print(self, message):

        if commands["dev_mode"]:
            print(self._tokens_count(message))

        self.send_api.send_log_to_api(message)

    def _send_model(self, messages):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Erro ao acessar a API: {str(e)}"

    def _verify_input(self):
        key = self.receive_toggle.monitor_logs()

        if key == "ATIVADO":
            return True
        else:
            return False

    def _listar_pastas(self):
        return [pasta for pasta in os.listdir(self.base_folder) if os.path.isdir(os.path.join(self.base_folder, pasta))]

    def _listar_jsons(self, pasta):
        caminho_pasta = os.path.join(self.base_folder, pasta)
        return [arq for arq in os.listdir(caminho_pasta) if arq.endswith(".json")]

    def _escolher_maquina(self, user):
        maquinas_disponiveis = machines

        prompt = f"""
        O usuário quer informações sobre "{user}". Aqui estão as máquinas disponíveis:
        {list(maquinas_disponiveis.keys())}
        
        Qual dessas máquinas é a mais relevante para a consulta do usuário?
        Responda apenas com o nome exato da máquina. Caso nenhuma máquina tenha sido fornecida pelo usuario. Responda apenas com "vazio".
        """

        machineName = self._send_model([{"role": "user", "content": prompt}])

        if machineName in maquinas_disponiveis:
            machine = MachineMap(machineName)
            especificMachine = machine.map()
            machine_info = OPCUAClient(commands["OPCUA_IP"], especificMachine, machineName)
            info = machine_info.connect()

            mensagem = f"Ótima escolha! Estou buscando informações sobre a máquina '{machineName}'..."
            mensagem = self._mensagem_personalizada(mensagem)
            self._log_and_print(mensagem)

            self._log_and_print(info)
        elif machineName == "vazio":
            user = self.receive_api.monitor_logs()
            self._log_and_print("Por favor, escolha uma máquina.")
            self._escolher_maquina(user)

    def _escolher_pasta(self, user):
        pastas_disponiveis = self._listar_pastas()

        prompt = f"""
        O usuário quer informações sobre "{user}" Abaixo está uma lista de setores disponíveis no JSON:
        {pastas_disponiveis}
        Qual desses setores melhor representa a intenção do usuário? Responda apenas com o nome exato do setor.
        """

        setor = self._send_model([{"role": "user", "content": prompt}])

        return setor if setor in pastas_disponiveis else False

    def _escolher_json(self, pasta):
        jsons_disponiveis = self._listar_jsons(pasta)

        prompt = f"""
        Forme uma frase legal falando que há estes itens disponíveis para consulta {jsons_disponiveis}. Quando for listar os itens, coloque apenas
        o nome dele, sem codigos e numeros. Também não coloque a extensão .json e nem aspas
        """

        choice_message = self._send_model([{"role": "user", "content": prompt}])
        self._log_and_print(choice_message)

        user = self.receive_api.monitor_logs()

        prompt = f"""
        O usuário quer informações sobre "{user}" Abaixo está uma lista de setores disponíveis no JSON:
        {jsons_disponiveis}
        Qual desses arquivos melhor representa a intenção do usuário? Responda apenas com o nome exato do arquivo.
        """

        json_escolhido = self._send_model([{"role": "user", "content": prompt}])

        return json_escolhido if json_escolhido in jsons_disponiveis else None
            

    def _complete(self, conteudo_json):
        return "\n".join([f"\n🔹 {chave.upper()}:\n{valor}" for chave, valor in conteudo_json.items()])
    
    def _identificar_contexto(self, user_input):  
        maquinas_disponiveis = machines

        prompt = f"""
        O usuário enviou a seguinte mensagem: "{user_input}"
        
        Classifique a intenção do usuário em uma das seguintes opções:
        - "máquina" se ele estiver pedindo informações sobre uma máquina específica: {list(maquinas_disponiveis.keys())}
        - "geral" se ele quiser informações gerais sobre os arquivos disponíveis
        Responda apenas com uma dessas palavras e nada mais.
        """

        resposta = self._send_model([{"role": "user", "content": prompt}])

        if resposta.strip().lower() == "máquina":
            self._escolher_maquina(user_input)
        else:
            pasta_escolhida = self._escolher_pasta(user_input)
            if pasta_escolhida:
                self._log_and_print(f"Beleza! Vou buscar informações em '{pasta_escolhida}'.")
                json_escolhido = self._escolher_json(pasta_escolhida)
                if json_escolhido:
                    self._log_and_print(f"Encontrei um arquivo que pode te ajudar: '{json_escolhido.replace('.json', '')}'!")
                    caminho_json = os.path.join(self.base_folder, pasta_escolhida, json_escolhido)
                    with open(caminho_json, "r", encoding="utf-8") as f:
                        conteudo_json = json.load(f)
                    response = self._complete(conteudo_json)
                    self._log_and_print(response)
                else:
                    self._log_and_print(commands['database_error'])
            else:
                self._log_and_print(commands['sector_error'])

        resposta = self._send_model([{"role": "user", "content": prompt}])
        return resposta.strip().lower()
    
    def _mensagem_personalizada(self, msg):
        prompt = f"""
        O usuário enviou a seguinte mensagem: "{msg}"
        
        Refaça a mensagem de maneira legal e divertida.
        """

        return self._send_model([{"role": "user", "content": prompt}])

    def _initial_message(self):
        prompt = f"""
        Faça uma mensagem educada e legal de "boas vindas ao modo de consulta Andritz".
        """

        return self._send_model([{"role": "user", "content": prompt}])
    

    def chat(self):
        while True:
            if self.restart_flag.is_set():
                self.restart_flag.clear()
                self._log_and_print("⚠️ Mudança detectada! Reiniciando verificações...")
                continue

            user = ""

            if self._verify_input():
                if self._check_restart(): continue
                
                self._log_and_print(self._initial_message())

                if self._check_restart(): continue
                
                user = self.receive_api.monitor_logs()

                if self._check_restart(): continue
                
                self._identificar_contexto(user)

                if self._check_restart(): continue

            else:
                if self._check_restart(): continue
                
                user = self.receive_api.monitor_logs()

                if self._check_restart(): continue
                
                if commands["dev_mode"] and user.lower() == "sair":
                    self._log_and_print(commands["exit_message"])
                    break

                response = self._send_model(self.history + [{"role": "user", "content": user}])
                
                if self._check_restart(): continue
                
                self.history.append({"role": "user", "content": user})
                self.history.append({"role": "assistant", "content": response})
                
                if self._check_restart(): continue
                
                self._log_and_print(f"{response}")

                if self._check_restart(): continue


if __name__ == "__main__":
    openai.api_key = commands["api_key"]
    chat_bot = ChatAndritz(api_key=openai.api_key, base_folder=r"C:\Users\Rafael\Desktop\Projeto 2025\Data\Limpo")
    chat_bot.chat()
