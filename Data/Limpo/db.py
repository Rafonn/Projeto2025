import os
import sqlite3

base_dir = os.path.dirname(os.path.abspath(__file__))

conn = sqlite3.connect(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db")
cursor = conn.cursor()

def sanitize_name(name):
    return "".join(c if c.isalnum() or c == "_" else "_" for c in name)

for item in os.listdir(base_dir):
    pasta_path = os.path.join(base_dir, item)
    
    if os.path.isdir(pasta_path):
        table_name = sanitize_name(item)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_content TEXT
            )
        """)

        for file in os.listdir(pasta_path):
            file_path = os.path.join(pasta_path, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"[ERRO AO LER ARQUIVO: {e}]"

                cursor.execute(f"""
                    INSERT INTO {table_name} (file_name, file_content)
                    VALUES (?, ?)
                """, (file, content))

conn.commit()
conn.close()

print("Tabelas criadas, arquivos inseridos e conteúdos salvos com sucesso.")
