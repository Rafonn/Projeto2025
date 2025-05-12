import pyodbc

class LastMessageFetcher:
    def __init__(self, user_id):
        self.server   = 'localhost'
        self.database = 'ConversationData'
        self.username = 'teste'
        self.password = 'Mpo69542507!'
        self.user_id  = user_id
        self.last_message_timestamp = None

        self.conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            'TrustServerCertificate=yes;'
        )

    def fetch_last_message(self):
        # Abre conexão e cursor
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 1 
                  userTimeStamp, 
                  userMessage 
                FROM user_logs 
                WHERE userId = ? 
                ORDER BY userTimeStamp DESC
            """, self.user_id)
            row = cursor.fetchone()

        if row:
            userTimeStamp, userMessage = row
            if userTimeStamp != self.last_message_timestamp:
                self.last_message_timestamp = userTimeStamp
                return userMessage
        return None
