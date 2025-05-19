import sys
import os

caminho_config = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maps"))
sys.path.append(caminho_config)

from products_ids import machines

class MachineMap:
    
    def __init__(self, machineName):
        self.machineName = machineName

    def map(self):
        especificMachine = machines[self.machineName]
        print(especificMachine)
        chaves = list(especificMachine.keys())
        
        valores_fixos = ["Código do pano", "Pano", "Cliente", "Urdição", "Posição", "Data prometida", "Picks", "Metros tecidos", "Total a tecer", "Último evento", "Observação", "Data de início de tecimento", "Hora de início de tecimento"]
        
        node_id_map = {chave: valor for chave, valor in zip(chaves, valores_fixos)}
        
        return node_id_map

if __name__ == "__main__":
    teste = MachineMap("TP100 / Tear 01")
    teste.map()
