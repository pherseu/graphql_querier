import sys
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QPlainTextEdit, 
                             QSplitter, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont  # <--- CORREÇÃO AQUI: QFont agora vem do QtGui

class GraphQLClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

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
        # Opcional: self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        top_layout.addWidget(self.token_input)

        # Botões de Ação
        self.btn_introspect = QPushButton('Atualizar Introspecção')
        self.btn_introspect.clicked.connect(self.run_introspection)
        top_layout.addWidget(self.btn_introspect)

        self.btn_execute = QPushButton('Executar Query ▶')
        self.btn_execute.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;")
        self.btn_execute.clicked.connect(self.run_query)
        top_layout.addWidget(self.btn_execute)

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
        
        self.setLayout(main_layout)

    # ==========================================
    # LÓGICA DE NEGÓCIO (Conecte seu backend aqui)
    # ==========================================
    
    def get_credentials(self):
        """Retorna os dados dos campos superiores"""
        return {
            'orgid': self.orgid_input.text().strip(),
            'token': self.token_input.text().strip()
        }

    def run_introspection(self):
        """Simula a busca do schema (Introspecção)"""
        creds = self.get_credentials()
        if not creds['orgid'] or not creds['token']:
            self.intro_editor.setPlainText("Erro: Preencha o Org ID e o Token.")
            return

        self.intro_editor.setPlainText("Buscando introspecção... (Conecte sua função de backend aqui)")

    def run_query(self):
        """Simula a execução da query"""
        creds = self.get_credentials()
        query = self.query_editor.toPlainText().strip()

        if not creds['orgid'] or not creds['token']:
            self.result_editor.setPlainText("Erro: Preencha o Org ID e o Token.")
            return
        
        if not query:
            self.result_editor.setPlainText("Erro: O campo de query está vazio.")
            return

        self.result_editor.setPlainText("Executando query... (Conecte sua função de backend aqui)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    
    gui = GraphQLClientGUI()
    gui.show()
    sys.exit(app.exec())