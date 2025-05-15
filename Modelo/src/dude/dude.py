from dude.controller import DudeConnectionBase

""" 
    Filtrar por:
    Status,
    Ativo,
    Data inicial 
"""

"""
    Completed
    New Request
    In Progress
"""

class DudeSolutions:

    def __init__(self, data, status):
        self.data = data
        self.status = status
    
    def getOrderBy(self):

        controller = DudeConnectionBase()
        ordens = controller.fetch_new_requests("Petropolis", self.data, self.status)
        orders = []
        
        for ordem in ordens:
            s = {
                "ID": ordem['IdOrdem'],
                "Nome": ordem['Nome'],
                "Problema": ordem.get('Problema', '—'),
                "Categoria": ordem['Categoria'],
                "Setor": ordem['Setor'],
                "Ativo": ordem['Ativo'],
                "Status": ordem['Status'],
                "Criado em": ordem['CriadoEm'],
                "Trabalho requisitado": ordem.get('TrabalhoReq', '').strip(),
                "Última modificação": ordem['UltimaModif'],
                "Data Esperada": ordem['DataEsperada'],
            }
            
            orders.append(s)
        
        return orders

if __name__ == "__main__":
    teste = DudeSolutions("2025-05-10T06:00:00", "Completed")
    print(teste.getOrderBy())