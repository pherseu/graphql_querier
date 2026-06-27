from PyQt6.QtCore import pyqtSignal, QThread


# Classe de worker multithread para que execute a lógica do software
class GraphQLWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, operation, orgid, token, query=None, variables=None):
        super().__init__()
        self.operation = operation
        self.orgid = orgid
        self.token = token
        self.query = query
        self.variables = variables

    def run(self):
        try:
            #TODO: roda toda a lógica do software
            print('teste')
        
        except Exception as e:
            self.error.emit(str(e))