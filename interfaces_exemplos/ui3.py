import sys
import json
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QPlainTextEdit, 
                             QSplitter, QFormLayout, QMessageBox, QStatusBar,
                             QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

class GraphQLWorker(QThread):
    """Thread worker para executar operações GraphQL sem travar a UI"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, operation, orgid, token, query=None):
        super().__init__()
        self.operation = operation  # 'introspect' ou 'query'
        self.orgid = orgid
        self.token = token
        self.query = query
    
    def run(self):
        try:
            # TODO: INTEGRE SEU BACKEND AQUI
            # Exemplo de como seria a integração real:
            # from seu_modulo import GraphQLClient
            # client = GraphQLClient(org_id=self.orgid, token=self.token)
            
            if self.operation == 'introspect':
                # schema = client.introspect()
                # Simulação:
                schema = {
                    "__schema": {
                        "queryType": {"name": "Query"},
                        "mutationType": {"name": "Mutation"},
                        "types": [
                            {"name": "Query", "kind": "OBJECT", "fields": [
                                {"name": "users", "type": {"name": "[User]"}},
                                {"name": "user", "type": {"name": "User"}}
                            ]},
                            {"name": "User", "kind": "OBJECT", "fields": [
                                {"name": "id", "type": {"name": "ID!"}},
                                {"name": "name", "type": {"name": "String!"}},
                                {"name": "email", "type": {"name": "String!"}}
                            ]},
                            {"name": "Mutation", "kind": "OBJECT", "fields": [
                                {"name": "createUser", "type": {"name": "User"}}
                            ]}
                        ]
                    }
                }
                result = json.dumps(schema, indent=2, ensure_ascii=False)
                self.finished.emit(result)
                
            elif self.operation == 'query':
                # result = client.execute(self.query)
                # Simulação:
                result_data = {
                    "data": {
                        "users": [
                            {"id": "1", "name": "João Silva", "email": "joao@exemplo.com"},
                            {"id": "2", "name": "Maria Santos", "email": "maria@exemplo.com"}
                        ]
                    }
                }
                result = json.dumps(result_data, indent=2, ensure_ascii=False)
                self.finished.emit(result)
                
        except Exception as e:
            self.error.emit(str(e))


class GraphQLClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        self.setWindowTitle('GraphQL Desktop Client')
        self.resize(1400, 850)

        # Fonte monoespaçada para as áreas de código e JSON
        mono_font = QFont("Consolas", 11) 
        mono_font.setStyleHint(QFont.StyleHint.Monospace)

        # ==========================================
        # 1. LAYOUT SUPERIOR (Autenticação e Ações)
        # ==========================================
        top_layout = QHBoxLayout()
        
        # Campo Org ID
        top_layout.addWidget(QLabel('Org ID:'))
        self.orgid_input = QLineEdit()
        self.orgid_input.setPlaceholderText('Digite o ID da organização...')
        top_layout.addWidget(self.orgid_input)

        # Campo Token
        top_layout.addWidget(QLabel('Token:'))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('Digite seu token de autenticação...')
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        top_layout.addWidget(self.token_input)

        # Checkbox para mostrar/ocultar token
        self.show_token_check = QCheckBox('Mostrar')
        self.show_token_check.stateChanged.connect(self.toggle_token_visibility)
        top_layout.addWidget(self.show_token_check)

        # Botões de Ação
        self.btn_introspect = QPushButton('Atualizar Introspecção')
        self.btn_introspect.clicked.connect(self.run_introspection)
        top_layout.addWidget(self.btn_introspect)

        self.btn_execute = QPushButton('Executar Query ▶')
        self.btn_execute.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;")
        self.btn_execute.clicked.connect(self.run_query)
        top_layout.addWidget(self.btn_execute)

        self.btn_clear = QPushButton('Limpar')
        self.btn_clear.clicked.connect(self.clear_all)
        top_layout.addWidget(self.btn_clear)

        # ==========================================
        # 2. LAYOUT INFERIOR (As 3 Colunas)
        # ==========================================
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Coluna da Esquerda: Introspecção
        self.intro_editor = QPlainTextEdit()
        self.intro_editor.setReadOnly(True)
        self.intro_editor.setFont(mono_font)
        self.intro_editor.setPlaceholderText('O schema e tipos do banco aparecerão aqui...')
        self.splitter.addWidget(self.intro_editor)

        # Coluna do Meio: Editor de Queries
        self.query_editor = QPlainTextEdit()
        self.query_editor.setFont(mono_font)
        self.query_editor.setPlaceholderText('Escreva sua query GraphQL aqui...\n\n{\n  users {\n    id\n    name\n  }\n}')
        self.splitter.addWidget(self.query_editor)

        # Coluna da Direita: Resultados
        self.result_editor = QPlainTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setFont(mono_font)
        self.result_editor.setPlaceholderText('O resultado da sua query aparecerá aqui...')
        self.splitter.addWidget(self.result_editor)

        # Define o tamanho inicial das colunas (Esquerda | Meio | Direita)
        self.splitter.setSizes([300, 600, 500])

        # ==========================================
        # 3. JUNTO TUDO NA JANELA PRINCIPAL
        # ==========================================
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.splitter)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage('Pronto.')
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)

    def setup_shortcuts(self):
        """Configura atalhos de teclado"""
        # Ctrl+Enter para executar query
        shortcut_execute = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_execute.activated.connect(self.run_query)
        
        # Ctrl+I para introspecção
        shortcut_introspect = QShortcut(QKeySequence("Ctrl+I"), self)
        shortcut_introspect.activated.connect(self.run_introspection)

    def toggle_token_visibility(self, state):
        """Mostra ou oculta o token"""
        if state == Qt.CheckState.Checked.value:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)

    def get_credentials(self):
        """Retorna os dados dos campos superiores"""
        return {
            'orgid': self.orgid_input.text().strip(),
            'token': self.token_input.text().strip()
        }

    def clear_all(self):
        """Limpa todos os campos de texto"""
        self.intro_editor.clear()
        self.query_editor.clear()
        self.result_editor.clear()
        self.status_bar.showMessage('Tudo limpo.')

    def run_introspection(self):
        """Executa a introspecção em thread separada"""
        creds = self.get_credentials()
        if not creds['orgid'] or not creds['token']:
            QMessageBox.warning(self, 'Atenção', 'Preencha o Org ID e o Token.')
            return

        self.status_bar.showMessage('Executando introspecção...')
        self.btn_introspect.setEnabled(False)
        
        # Cria e inicia a thread worker
        self.worker = GraphQLWorker('introspect', creds['orgid'], creds['token'])
        self.worker.finished.connect(self.on_introspection_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def run_query(self):
        """Executa a query em thread separada"""
        creds = self.get_credentials()
        query = self.query_editor.toPlainText().strip()

        if not creds['orgid'] or not creds['token']:
            QMessageBox.warning(self, 'Atenção', 'Preencha o Org ID e o Token.')
            return
        
        if not query:
            QMessageBox.warning(self, 'Atenção', 'O campo de query está vazio.')
            return

        self.status_bar.showMessage('Executando query...')
        self.btn_execute.setEnabled(False)
        
        # Cria e inicia a thread worker
        self.worker = GraphQLWorker('query', creds['orgid'], creds['token'], query)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_introspection_finished(self, result):
        """Callback quando introspecção termina com sucesso"""
        self.intro_editor.setPlainText(result)
        self.status_bar.showMessage('Introspecção concluída.')
        self.btn_introspect.setEnabled(True)

    def on_query_finished(self, result):
        """Callback quando query termina com sucesso"""
        self.result_editor.setPlainText(result)
        self.status_bar.showMessage('Query executada com sucesso.')
        self.btn_execute.setEnabled(True)

    def on_error(self, error_msg):
        """Callback quando ocorre erro na thread"""
        QMessageBox.critical(self, 'Erro', f'Falha na operação:\n{error_msg}')
        self.status_bar.showMessage('Erro na execução.')
        self.btn_introspect.setEnabled(True)
        self.btn_execute.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    
    gui = GraphQLClientGUI()
    gui.show()
    sys.exit(app.exec())