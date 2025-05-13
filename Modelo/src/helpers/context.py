import pyodbc

class Context:
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

    def listar_tabelas_sql_server(self):
        try:
            query = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_SCHEMA = 'dbo';
            """

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                tabelas = [row.TABLE_NAME for row in cursor.fetchall()]

        except Exception as e:
            return f"Erro ao listar tabelas: {e}"

        return tabelas
    
    def consultar_tabela(self, nome_tabela):
        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                tabela_ident = f"[dbo].[{nome_tabela}]"
                cur.execute(f"SELECT * FROM {tabela_ident}")
                cols = [col[0] for col in cur.description]
                rows = cur.fetchall()
                resultados = [dict(zip(cols, row)) for row in rows]

            return resultados

        except Exception as e:
            return f"Erro ao consultar a tabela '{nome_tabela}': {e}"
    
if __name__ == "__main__":
    classe = Context()
    print(classe.consultar_tabela("Mantas"))