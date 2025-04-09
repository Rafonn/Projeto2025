import openai
import os
import json
import tiktoken
import time
import threading
import sqlite3

from api.send import Send
from api.receive import Receive
from api.toggleReceive import ToggleReceive
from data.machines_ids import machines
from data.machineName import MachineName
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

    def _listar_tabelas(self):
        try:
            conn = sqlite3.connect(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db")
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = [row[0] for row in cursor.fetchall()]

            conn.close()
            return tabelas
        except Exception as e:
            return f"Erro ao listar tabelas: {e}"
    
    def _consultar_tabela(self, nome_tabela):
        try:
            conn = sqlite3.connect(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db")
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = [col[1] for col in cursor.fetchall()]

            cursor.execute(f"SELECT * FROM {nome_tabela}")
            dados = cursor.fetchall()

            resultados = []
            for row in dados:
                resultado = {}
                for idx, col in enumerate(colunas):
                    resultado[col] = row[idx]
                resultados.append(resultado)

            conn.close()
            return resultados
        except Exception as e:
            return f"Erro ao consultar a tabela '{nome_tabela}': {e}"

    def _listar_file_names(self, tabela):
        try:
            conn = sqlite3.connect("machines_data.db")
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = [col[1] for col in cursor.fetchall()]
            if "file_name" not in colunas:
                return []

            cursor.execute(f"SELECT DISTINCT file_name FROM {tabela}")
            arquivos = cursor.fetchall()

            nomes_limpos = [os.path.splitext(row[0])[0] for row in arquivos]

            conn.close()
            return nomes_limpos
        except Exception as e:
            print(f"Erro ao listar file_names da tabela '{tabela}': {e}")
            return []

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

            machine_info = MachineName(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db", machineName)
            info = machine_info.getMachineInfo()
            print(info)

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
    
    def _identificar_contexto(self, user_input):  #Continuar com as máquinas
        tabelas = self._listar_tabelas()

        prompt = f"""
        O usuário enviou a seguinte mensagem: "{user_input}"
        Aqui estão as tabelas disponíveis no banco: {tabelas}

        Qual dessas tabelas o usuário está querendo consultar?
        Responda apenas com o nome exato da tabela sem "ç" e acento. Para nomes com espaço, faça os espaços com "_" e cada palvra começa com letra maiúscula. Se não identificar nenhuma, 
        responda com "vazio". Caso a mensagem contenha uma dessas palavras: {machines}. responda APENAS com "machine".
        """

        tabela_escolhida = self._send_model([{"role": "user", "content": prompt}])

        if tabela_escolhida in tabelas:
            dados = self._consultar_tabela(tabela_escolhida)

            if not dados:
                self._log_and_print("A tabela está vazia.")
                return

            prompt = f"""
            Gere uma resposta amigável com os dados da tabela '{tabela_escolhida}'.
            Formate de forma fácil de ler para humanos:
            {json.dumps(dados, indent=2, ensure_ascii=False)}
            """

            resposta = self._send_model([{"role": "user", "content": prompt}])
            self._log_and_print(resposta)
        elif tabela_escolhida.lower() == "machine":
            dados = self._escolher_maquina(user_input)
        else:
            self._log_and_print("Não consegui identificar nenhuma tabela com esse nome. Pode tentar de novo?")
    
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
