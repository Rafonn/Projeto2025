import json

class ReadData:
    def __init__(self, arquivo_json):
        self.arquivo_json = arquivo_json

    def load_json(self):
        with open(self.arquivo_json, "r", encoding="utf-8") as f:
            return json.load(f)

    def text_per_key(self, chave):
        if chave in self.dados:
            return self.dados[chave]
        else:
            return "Chave não encontrada"
