import openai
import json
from data import ReadData
from commands import commands

class ChatAndritz:
    def __init__(self, api_key, json_file):
        self.api_key = api_key
        openai.api_key = self.api_key
        read_data = ReadData(json_file)
        self.json_data = read_data.load_json()
        self.history = [{"role": "system", "content": commands["initial"]}]

    def _send_model(self, messages):
        """ Envia mensagens ao modelo GPT e retorna a resposta. """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Erro ao acessar a API: {str(e)}"

    def _find_key_in_json(self, user_topic):
        """ Tenta encontrar a chave mais relevante no JSON. """
        prompt = f"""
        O usuário quer informações sobre "{user_topic}".
        Abaixo está uma lista de chaves disponíveis no JSON:
        {list(self.json_data.keys())}
        Qual dessas chaves melhor representa a intenção do usuário? Responda apenas com o nome exato da chave.
        """

        key = self._send_model([{"role": "user", "content": prompt}])
        return f"Faça um resumo sobre: {self.json_data[key]}" if key in self.json_data else commands["database_error"]

    def _verify_input(self):
        """ Verifica a senha antes de permitir acesso ao modo de busca no JSON. """
        key_security = input(commands["key_security_message"]).strip().lower()
        return key_security == "andritz"

    def chat(self):
        """ Loop principal do chatbot. """
        while True:
            print(f"\n{commands['exit_warn']}")
            question = ""

            if self._verify_input():
                topic = input(commands["topic_message"]).strip()
                response = self._find_key_in_json(topic)
            else:
                question = input("Você: ").strip()
                if question.lower() == "sair":
                    print(commands["exit_message"])
                    break

                response = self._send_model(self.history + [{"role": "user", "content": question}])
            
            self.history.append({"role": "user", "content": question})
            self.history.append({"role": "assistant", "content": response})
            
            print(f"GPT: {response}")

if __name__ == "__main__":
    openai.api_key = commands["api_key"]
    chat_bot = ChatAndritz(api_key=openai.api_key, json_file="../manual_estruturado.json")
    chat_bot.chat()
