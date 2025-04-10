import sqlite3

nomes_personalizados = {
    "machine_name": "Equipamento",
    "Parado___Rodando": "Parado / Rodando",
    "Tempo_parado_atual": "Tempo parado atual",
    "Ultimo_tempo_parado": "Ultimo tempo parado",
    "Tempo_parado_do_dia": "Tempo parado do dia",
    "Tempo_parado_do_dia_anterior": "Tempo parado do dia anterior",
    "Tempo_parado_na_semana_anterior": "Tempo parado na semana anterior",
    "Eficiencia_atual": "Eficiência",
    "Batidas": "Batidas do dia",
}

class MachineName:
    def __init__(self, dbFile, name):
        self.dbFile = dbFile
        self.name = name

    def getMachineInfo(self):
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines WHERE machine_name = ?", (self.name,))
        row = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]
        conn.close()

        linhas = []
        for col, val in zip(column_names, row):
            nome_exibido = nomes_personalizados.get(col, col)
            if col == "Parado___Rodando":
                val = "Parado" if val == 0 else "Rodando" if val == 1 else val
            linhas.append(f"{nome_exibido}: {val}")
        
        result = '\n'.join(linhas)
        return result
    
if __name__ == "__main__":
    machineName = MachineName(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db", "CLT1")
    machineName.getMachineInfo()