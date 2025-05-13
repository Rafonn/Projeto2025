from controller import DudeConnectionBase

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

    def __init__(self, status, ativo, data):
        self.status = status
        self.ativo = ativo
        self.data = data
    
    def getOrderBy(self):
        controller = DudeConnectionBase()
        ordens = controller.fetch_new_requests("Petropolis", self.status, self.data)
        for ordem in ordens:
            print (f"{ordem['IdOrdem']}\n")

if __name__ == "__main__":
    teste = DudeSolutions("Completed", "teste", "2025-05-02T07:22:00")
    teste.getOrderBy()