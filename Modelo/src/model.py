import openai
import os
import json
import tiktoken
import time
import threading
import sqlite3
from multiprocessing import Process, set_start_method

from api.receive import LastMessageFetcher
from api.toggleReceive import ToggleButtonStatus
from data.machines_ids import machines
from data.machineName import MachineName
from data.conversation import Conversation
from commands import commands

class RestartException(Exception):
    pass

class ChatAndritz:
    def __init__(self, api_key, base_folder, user_id):
        self.user_id = user_id
        self.api_key = api_key
        openai.api_key = self.api_key

        self.message_fetcher = LastMessageFetcher(self.user_id)

        self.user_folder = os.path.join(base_folder, user_id)
        os.makedirs(self.user_folder, exist_ok=True)

        self.receive_toggle = ToggleButtonStatus(self.user_id)

        self.history = [{"role": "system", "content": commands["initial"]}]

        self.verify_state = self._verify_input()
        self.restart_flag = threading.Event()
        self.monitor_thread = threading.Thread(target=self._monitor_input, daemon=True)
        self.monitor_thread.start()
    
    def _tokens_count(self, messages, model="gpt-3.5-turbo"):
        encoding = tiktoken.encoding_for_model(model)
        return sum(len(encoding.encode(m["content"])) for m in messages)
    
    def _monitor_input(self):
        while True:
            current = self._verify_input()
            if current != self.verify_state:
                self.verify_state = current
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
        conv = Conversation(message, self.user_id)
        conv.botResponse()

    def _send_model(self, messages):
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Erro ao acessar a API: {e}"

    def _verify_input(self):
        key = self.receive_toggle.fetch_status()
        return key

    def _listar_tabelas(self):
        try:
            conn = sqlite3.connect(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db")
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = [r[0] for r in cur.fetchall()]
            conn.close()
            return tabelas
        except Exception as e:
            return f"Erro ao listar tabelas: {e}"
    
    def _consultar_tabela(self, nome_tabela):
        try:
            conn = sqlite3.connect(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db")
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({nome_tabela})")
            cols = [c[1] for c in cur.fetchall()]
            cur.execute(f"SELECT * FROM {nome_tabela}")
            rows = cur.fetchall()
            conn.close()

            resultados = []
            for r in rows:
                d = {cols[i]: r[i] for i in range(len(cols))}
                resultados.append(d)
            return resultados
        except Exception as e:
            return f"Erro ao consultar a tabela '{nome_tabela}': {e}"

    def _listar_file_names(self, tabela):
        try:
            conn = sqlite3.connect("machines_data.db")
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({tabela})")
            cols = [c[1] for c in cur.fetchall()]
            if "file_name" not in cols:
                return []
            cur.execute(f"SELECT DISTINCT file_name FROM {tabela}")
            files = [os.path.splitext(r[0])[0] for r in cur.fetchall()]
            conn.close()
            return files
        except Exception as e:
            print(f"Erro ao listar file_names da tabela '{tabela}': {e}")
            return []

    def _escolher_maquina(self, user):
        maquinas_disponiveis = machines
        prompt = f"""
        O usuário quer informações sobre "{user}". Aqui estão as máquinas disponíveis:
        {list(maquinas_disponiveis.keys())}
        Qual dessas máquinas é a mais relevante? Responda apenas com o nome exato da máquina ou "vazio".
        """
        machineName = self._send_model([{"role": "user", "content": prompt}])
        if machineName in maquinas_disponiveis:
            mi = MachineName(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db", machineName)
            info = mi.getMachineInfo()
            mensagem = f"Ótima escolha! Buscando informações sobre '{machineName}'..."
            mensagem = self._mensagem_personalizada(mensagem)
            self._log_and_print(mensagem)
            self._log_and_print(info)

    def _escolher_pasta(self, user):
        pastas = self._listar_pastas()
        prompt = f"""
        O usuário quer informações sobre "{user}". Setores disponíveis:
        {pastas}
        Qual setor melhor representa a intenção? Responda só com o nome exato.
        """
        setor = self._send_model([{"role": "user", "content": prompt}])
        return setor if setor in pastas else False
    
    def _identificar_contexto(self, user_input):
        tabelas = self._listar_tabelas()
        prompt = f"""
        O usuário enviou: "{user_input}".
        Tabelas disponíveis: {tabelas}
        Qual tabela ele quer consultar? Responda só com o nome exato (ou "vazio"). 
        Se a mensagem contiver alguma chave de {machines}, responda "machine".
        """
        escolha = self._send_model([{"role": "user", "content": prompt}])
        if escolha in tabelas and escolha.lower() != "machine":
            dados = self._consultar_tabela(escolha)
            if not dados:
                self._log_and_print("A tabela está vazia.")
                return
            prompt2 = f"""
            Gere uma resposta amigável com os dados da tabela '{escolha}':
            {json.dumps(dados, indent=2, ensure_ascii=False)}
            """
            resp = self._send_model([{"role": "user", "content": prompt2}])
            self._log_and_print(resp)
        elif escolha.lower() == "machine":
            self._escolher_maquina(user_input)
        else:
            self._log_and_print("Não identifiquei tabela. Pode tentar de novo?")

    def _mensagem_personalizada(self, msg):
        prompt = f"""
        Refaça a seguinte mensagem de forma legal e divertida, sem aspas:
        {msg}
        """
        return self._send_model([{"role": "user", "content": prompt}])
    
    def _esperar_entrada_usuario(self):
        while not self.restart_flag.is_set():
            nova = self.message_fetcher.fetch_last_message()
            if nova:
                return nova

            """ # Opcional: se quiser fallback ao arquivo
            user_file = self.receive_api.monitor_logs(restart_flag=self.restart_flag, timeout=0.5)
            if self.restart_flag.is_set():
                raise RestartException("Mudança detectada")
            if user_file:
                return user_file """

            time.sleep(0.5)

    def chat(self):
        while True:
            try:
                while True:
                    if self.restart_flag.is_set():
                        raise RestartException()

                    if self._verify_input():
                        user = self._esperar_entrada_usuario()
                        self._identificar_contexto(user)
                    else:
                        user = self._esperar_entrada_usuario()
                        print(user)
                        if commands["dev_mode"] and user.lower() == "sair":
                            self._log_and_print(commands["exit_message"])
                            return
                        response = self._send_model(self.history + [{"role": "user", "content": user}])
                        self.history.append({"role": "user", "content": user})
                        self.history.append({"role": "assistant", "content": response})
                        self._log_and_print(response)
            except RestartException:
                self._log_and_print("⚠️ Mudança detectada! Reiniciando verificações...")
                self.restart_flag.clear()

def start_chat_for_user(user_id, api_key, base_folder):
    try:
        bot = ChatAndritz(api_key=api_key, base_folder=base_folder, user_id=user_id)
        bot.chat()
    except Exception as e:
        print(f"[{user_id}] erro: {e!r}", flush=True)

if __name__ == "__main__":
    try:
        set_start_method('spawn')
    except RuntimeError:
        pass

    # só aqui defino a chave e a pasta
    openai.api_key = commands["api_key"]
    base_folder = r"C:\Users\Rafael\Desktop\Projeto 2025\Data\Limpo"

    user_ids = [
        "251dc48b-fed5-49b2-b022-4c0f585af2e8",
    ]

    processes = []
    for uid in user_ids:
        p = Process(
            target=start_chat_for_user,
            args=(uid, openai.api_key, base_folder),
            name=f"ChatAndritz-{uid}"
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
