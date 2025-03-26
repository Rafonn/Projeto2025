import openai
import os
import json
from data import ReadData
from commands import commands
import sys

class ChatAndritz:
    def __init__(self, api_key, base_folder):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.base_folder = base_folder
        self.history = [{"role": "system", "content": commands["initial"]}]

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
        key_security = input(f'{commands["key_security_message"]}\n{commands['usuario']}').strip().lower()

        if(commands["dev_mode"] == True and key_security == "sair"):
            sys.exit()

        return key_security == "andritz"

    def _listar_pastas(self):
        return [pasta for pasta in os.listdir(self.base_folder) if os.path.isdir(os.path.join(self.base_folder, pasta))]

    def _listar_jsons(self, pasta):
        caminho_pasta = os.path.join(self.base_folder, pasta)

        return [arq for arq in os.listdir(caminho_pasta) if arq.endswith(".json")]

    def _escolher_pasta(self):
        pastas_disponiveis = self._listar_pastas()

        setor_usuario = input(f"{commands['nome']}{commands["sector"]}\n{commands['usuario']}").strip()

        prompt = f"""
        O usuário quer informações sobre "{setor_usuario}" Abaixo está uma lista de setores disponíveis no JSON:
        {pastas_disponiveis}
        Qual desses setores melhor representa a intenção do usuário? Responda apenas com o nome exato do setor.
        """

        setor = self._send_model([{"role": "user", "content": prompt}])

        return setor if setor in pastas_disponiveis else None

    def _escolher_json(self, pasta):
        jsons_disponiveis = self._listar_jsons(pasta)

        prompt = f"""
        Forme uma frase legal e humorada falando que há estes itens disponíveis para consulta {jsons_disponiveis}. Quando for listar os itens, coloque apenas
        o nome dele, sem codigos e numeros. tambem não coloque a extensão .json
        """

        choice_message = self._send_model([{"role": "user", "content": prompt}])
        
        json_usuario = input(f"{commands['nome']}{choice_message.strip('"')}\n{commands['usuario']}").strip()

        prompt = f"""
        O usuário quer informações sobre "{json_usuario}" Abaixo está uma lista de setores disponíveis no JSON:
        {jsons_disponiveis}
        Qual desses arquivos melhor representa a intenção do usuário? Responda apenas com o nome exato do arquivo.
        """

        json_escolhido = self._send_model([{"role": "user", "content": prompt}])

        return json_escolhido if json_escolhido in jsons_disponiveis else None

    def _resumir_ou_completo(self, conteudo_json):
        escolha = input(f"{commands['nome']}{commands["resume/complete"]}\n{commands['usuario']}").strip().lower()

        if escolha == "resumo":
            prompt = f"Faça um resumo do seguinte conteúdo mostrando as informações mais importantes dos tópicos:\n{json.dumps(conteudo_json, ensure_ascii=False, indent=4)}"
            return self._send_model([{"role": "user", "content": prompt}])
        else:
            return "\n".join([f"\n🔹 {chave.upper()}:\n{valor}" for chave, valor in conteudo_json.items()])

    def chat(self):
        while True:
            print(f"\n{commands['exit_warn']}")
            question = ""

            if self._verify_input():
                pasta_escolhida = self._escolher_pasta()

                if not pasta_escolhida:
                    print(f"{commands['nome']}{commands["sector_error"]}\n")

                    continue
                
                json_escolhido = self._escolher_json(pasta_escolhida)

                if not json_escolhido:
                    print(f"{commands['nome']}{commands["database_error"]}\n")

                    continue
                
                caminho_json = os.path.join(self.base_folder, pasta_escolhida, json_escolhido)
                
                with open(caminho_json, "r", encoding="utf-8") as f:
                    conteudo_json = json.load(f)
                
                response = self._resumir_ou_completo(conteudo_json)
            else:
                print(f"{commands["web_mode"]}\n")

                question = input(f"{commands['usuario']}").strip()

                if (commands["dev_mode"] == True and question.lower() == "sair"):
                    print(commands["exit_message"])
                    break

                response = self._send_model(self.history + [{"role": "user", "content": question}])
            
            self.history.append({"role": "user", "content": question})
            self.history.append({"role": "assistant", "content": response})
            
            print(f"{commands['nome']}{response}")

if __name__ == "__main__":
    openai.api_key = commands["api_key"]
    chat_bot = ChatAndritz(api_key=openai.api_key, base_folder=r"C:\Users\Rafael\Desktop\Projeto 2025\Data\Limpo")
    chat_bot.chat()