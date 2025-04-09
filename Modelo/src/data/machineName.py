import sqlite3

class MachineName:
    def __init__(self, dbFile, name):
        self.dbFile = dbFile
        self.name = name
    
    def getMachineInfo(self):
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines WHERE machine_name = ?", (self.name,))
        row = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]
        result = dict(zip(column_names, row))
        formatted_str = '\n'.join(f"{key}: {value}" for key, value in result.items()) 
        return formatted_str
    
if __name__ == "__main__":
    machineName = MachineName(r"C:\Users\Rafael\Desktop\Projeto 2025\DB\DadosAndritz.db", "CLT1")
    machineName.getMachineInfo()