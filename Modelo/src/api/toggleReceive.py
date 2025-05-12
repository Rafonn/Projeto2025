import pyodbc

class ToggleButtonStatus:
    def __init__(self, user_id):
        self.user_id = user_id
        self.conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost;'
            'DATABASE=ConversationData;'
            'UID=teste;'
            'PWD=Mpo69542507!;'
            'TrustServerCertificate=yes;'
        )
        self._ensure_table()

    def _ensure_table(self):
        with pyodbc.connect(self.conn_str, autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sys.tables 
                WHERE name = 'andritzButton_logs'
            )
            BEGIN
                CREATE TABLE andritzButton_logs (
                    userId      NVARCHAR(50) PRIMARY KEY,
                    buttonState BIT         NOT NULL DEFAULT(0),
                    updated_at    DATETIMEOFFSET NOT NULL 
                                   DEFAULT SYSDATETIMEOFFSET()
                );
            END
            """)

    def fetch_status(self) -> bool:
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT buttonState FROM andritzButton_logs WHERE userId = ?",
                self.user_id
            )
            row = cursor.fetchone()

            if(row[0] == 1):
                boolButton = True
            else:
                boolButton = False

        return boolButton

if __name__ == "__main__":
    t = ToggleButtonStatus("251dc48b-fed5-49b2-b022-4c0f585af2e8")
    estado = t.fetch_status()
    print(f"Toggle para 251dc48b-fed5-49b2-b022-4c0f585af2e8 está {'ON' if estado else 'OFF'}")
