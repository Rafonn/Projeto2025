import pyodbc
from datetime import datetime

class Conversation:
    def __init__(self, message, user_id):
        self.message = message
        self.user_id = user_id
        self.conn = self.connect_to_db()

    def connect_to_db(self):
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=ConversationData;'
            'UID=teste;'
            'PWD=Mpo69542507!;'
            'TrustServerCertificate=yes;'
        )
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        cursor.execute("""
        IF NOT EXISTS (
            SELECT * 
            FROM sys.tables 
            WHERE name = 'bot_logs'
        )
        BEGIN
            CREATE TABLE bot_logs (
                id INT IDENTITY(1,1) PRIMARY KEY,
                userId NVARCHAR(50) NOT NULL,
                botMessage NVARCHAR(MAX) NOT NULL,
                userTimeStamp DATETIMEOFFSET NOT NULL 
                    DEFAULT SYSDATETIMEOFFSET()
            );
        END
        """)
        return conn

    def botResponse(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO bot_logs (userId, botMessage)
            OUTPUT INSERTED.botTimeStamp
            VALUES (?, ?);
        """, (self.user_id, self.message))
        inserted_ts = cursor.fetchone()[0]
        # Commit automático por autocommit=True, mas se precisar:
        # self.conn.commit()
        return {
            "botMessage": self.message,
            "botTimeStamp": inserted_ts
        }

    def close(self):
        self.conn.close()

# Exemplo de uso:
if __name__ == "__main__":
    conv = Conversation("Olá, mundo!", "usuario123")
    result = conv.botResponse()
    print(f"Bot enviou: {result['botMessage']} às {result['botTimeStamp']}")
    conv.close()
