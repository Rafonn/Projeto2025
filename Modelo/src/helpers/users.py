import pyodbc

class SqlServerUserFetcher:

    def __init__(self):
        self.server = "localhost"
        self.database = "ConversationData"
        self.username = "teste"
        self.password = "Mpo69542507!"
        self.table_name = "user_logs"
        self.id_column = "userId"
        self.driver = "{ODBC Driver 17 for SQL Server}"

    def _get_connection(self):
        conn_str = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )
        return pyodbc.connect(conn_str)

    def get_user_ids(self) -> list:
        query = f"SELECT DISTINCT {self.id_column} FROM {self.table_name}"
        ids = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                ids = [row[0] for row in cursor.fetchall()]
        except pyodbc.Error as e:
            print(f"Erro ao acessar o banco: {e}")
        return ids

if __name__ == "__main__":
    fetcher = SqlServerUserFetcher()
    user_ids = fetcher.get_user_ids()
    print("IDs de usuários encontrados:", user_ids)
