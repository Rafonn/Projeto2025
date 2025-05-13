import os
import pyodbc

base_dir = os.path.dirname(os.path.abspath(__file__))

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=ConversationData;"
    "UID=teste;"
    "PWD=Mpo69542507!;"
    "TrustServerCertificate=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def sanitize_name(name):
    return "".join(c if c.isalnum() or c == "_" else "_" for c in name)

for item in os.listdir(base_dir):
    pasta_path = os.path.join(base_dir, item)
    if not os.path.isdir(pasta_path):
        continue

    table_name = sanitize_name(item)
    full_table = f"[dbo].[{table_name}]"

    cursor.execute(f"""
    IF OBJECT_ID(N'{full_table}', N'U') IS NULL
    BEGIN
        CREATE TABLE {full_table} (
            id          INT IDENTITY(1,1) PRIMARY KEY,
            file_name   NVARCHAR(255) NOT NULL,
            file_content NVARCHAR(MAX) NULL
        );
    END
    """)
    conn.commit()

    for file in os.listdir(pasta_path):
        file_path = os.path.join(pasta_path, file)
        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"[ERRO AO LER ARQUIVO: {e}]"

        cursor.execute(f"""
            INSERT INTO {full_table} (file_name, file_content)
            VALUES (?, ?)
        """, file, content)

    conn.commit()

cursor.close()
conn.close()

print("Tabelas criadas, arquivos inseridos e conteúdos salvos com sucesso no SQL Server.")
