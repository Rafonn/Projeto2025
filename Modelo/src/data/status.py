import sqlite3
from opcua import Client
from machines_ids import machines


class OPCUAClient:
    def __init__(self, url, machines_dict, db_file=r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db"):
        self.url = url
        self.client = Client(url)
        self.db_file = db_file
        self.machines = machines_dict
        self.setup_database()

    def connect(self):
        try:
            self.client.connect()
            return self.run()
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return "As máquinas estão fora do ar, desculpe o transtorno. Tente novamente mais tarde."

    def disconnect(self):
        self.client.disconnect()

    def read_tag(self, node_id):
        try:
            node = self.client.get_node(node_id)
            value = node.get_value()
            return value
        except Exception as e:
            print(f"Erro ao ler a tag {node_id}: {e}")
            return None

    def setup_database(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                machine_name TEXT PRIMARY KEY
            )
        """)
        self.conn.commit()

    def save_data_to_db(self, machine_name, values):
        try:
            for key in values.keys():
                column = key.replace(" ", "_").replace("/", "_")
                try:
                    self.cursor.execute(f"ALTER TABLE machines ADD COLUMN '{column}'")
                except sqlite3.OperationalError:
                    pass

            columns = ", ".join([f"'{key.replace(' ', '_').replace('/', '_')}'" for key in values])
            placeholders = ", ".join(["?"] * len(values))
            update_clause = ", ".join([f"{col}=excluded.{col}" for col in columns.split(", ")])

            values_list = list(values.values())

            self.cursor.execute(f"""
                INSERT INTO machines (machine_name, {columns})
                VALUES (?, {placeholders})
                ON CONFLICT(machine_name) DO UPDATE SET {update_clause}
            """, [machine_name] + values_list)

            self.conn.commit()
        except Exception as e:
            print(f"Erro ao salvar os dados no banco de dados: {e}")

    def run(self):
        result = ""
        for machine_name, node_map in self.machines.items():
            values = {}
            for node_id, tag_label in node_map.items():
                value = self.read_tag(node_id)
                if value is not None:
                    values[tag_label] = value
                    result += f"{machine_name} - {tag_label}: {value}\n"

            if values:
                self.save_data_to_db(machine_name, values)

        return result


if __name__ == "__main__":
    opcua_client = OPCUAClient("opc.tcp://10.243.74.204:5000", machines)
    opcua_client.connect()
    opcua_client.disconnect()
