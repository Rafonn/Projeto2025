import json
import time
from opcua import Client

class OPCUAClient:
    def __init__(self, url, node_id_map, machineName, output_file="data.json"):
        self.url = url
        self.machineName = machineName
        self.client = Client(url)
        self.output_file = output_file
        self.tag_groups = {
            machineName: list(node_id_map.keys())
        }
        
        self.node_id_map = node_id_map

    def connect(self):
        try:
            self.client.connect()
            return self.run()
        except Exception as e:
            return "As máquinas estão fora do ar, desculpe o transtorno. Tente novamente mais tarde."

    def disconnect(self):
        self.client.disconnect()

    def read_tag(self, node_id):
        try:
            node = self.client.get_node(node_id)
            value = node.get_value()
            print(f"Valor da tag {node_id}: {value}")
            return value
        except Exception as e:
            print(f"Erro ao ler a tag {node_id}: {e}")
            return None

    def save_data_to_json(self, tag_name, values):
        try:
            try:
                with open(self.output_file, "r") as file:
                    existing_data = json.load(file)
            except FileNotFoundError:
                existing_data = {}

            existing_data[tag_name] = {
                "values": values,
                "timestamp": time.time()
            }

            with open(self.output_file, "w") as file:
                json.dump(existing_data, file, indent=4)
        except Exception as e:
            print(f"Erro ao salvar os dados em JSON: {e}")

    def run(self):
        result = ""
        for tag_name, node_ids in self.tag_groups.items():
            values = {}
            for node_id in node_ids:
                value = self.read_tag(node_id)
                if value is not None:
                    tag_label = self.node_id_map.get(node_id, node_id)
                    values[tag_label] = value
                    result += f"{tag_label}: {value}\n"

            if values:
                self.save_data_to_json(tag_name, values)
        
        return result


if __name__ == "__main__":
    teste = MachineMap("CLT1")
    
    opcua_client = OPCUAClient("opc.tcp://10.243.74.204:5000", teste.map(), "CLT1")
    opcua_client.connect()
