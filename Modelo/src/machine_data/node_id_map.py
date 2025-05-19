import sys
import os

caminho_config = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maps"))
sys.path.append(caminho_config)

from machine_data.machines_ids import machines

class MachineMap:
    
    def __init__(self, machineName):
        self.machineName = machineName

    def map(self):
        especificMachine = machines[self.machineName]
        print(especificMachine)
        chaves = list(especificMachine.keys())
        
        valores_fixos = ["Parado / Rodando", "Tempo parado atual", "Ultimo tempo parado", "Tempo parado do dia", "Tempo parado do dia anterior", "Tempo parado na semana anterior", "Eficiencia atual", "Batidas"]
        
        node_id_map = {chave: valor for chave, valor in zip(chaves, valores_fixos)}
        
        return node_id_map

if __name__ == "__main__":
    teste = MachineMap("CLT1")
    teste.map()
