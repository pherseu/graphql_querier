import sys
import json
import threading
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QPlainTextEdit, 
                             QSplitter, QMessageBox, QStatusBar, QCheckBox,
                             QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QTextCharFormat, QColor

class GraphQLWorker(QThread):
    """Thread worker para executar operações GraphQL sem travar a UI"""
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
            # TODO: INTEGRE SEU BACKEND AQUI
            # from seu_modulo import GraphQLClient
            # client = GraphQLClient(org_id=self.orgid, token=self.token)
            
            if self.operation == 'introspect':
                # Simulação de introspecção
                schema = {
                    "__schema": {
                        "queryType": {"name": "Query"},
                        "mutationType": {"name": "Mutation"},
                        "types": [
                            {"name": "Query", "kind": "OBJECT", "fields": [
                                {"name": "users", "type": {"name": "[User]"}},
                                {"name": "user", "type": {"name": "User"}},
                                {"name": "posts", "type": {"name": "[Post]"}}
                            ]},
                            {"name": "User", "kind": "OBJECT", "fields": [
                                {"name": "id", "type": {"name": "ID!"}},
                                {"name": "name", "type": {"name": "String!"}},
                                {"name": "email", "type": {"name": "String!"}},
                                {"name": "posts", "type": {"name": "[Post]"}}
                            ]},
                            {"name": "Post", "kind": "OBJECT", "fields": [
                                {"name": "id", "type": {"name": "ID!"}},
                                {"name": "title", "type": {"name": "String!"}},
                                {"name": "content", "type": {"name": "String!"}},
                                {"name": "author", "type": {"name": "User"}}
                            ]},
                            {"name": "Mutation", "kind": "OBJECT", "fields": [
                                {"name": "createUser", "type": {"name": "User"}},
                                {"name": "createPost", "type": {"name": "Post"}}
                            ]}
                        ]
                    }
                }
                result = json.dumps(schema, indent=2, ensure_ascii=False)
                self.finished.emit(result)
                
            elif self.operation == 'query':
                # Simulação de execução de query
                result_data = {
                    "data": {
                        "users": [
                            {"id": "1", "name": "João Silva", "email": "joao@exemplo.com"},
                            {"id": "2", "name": "Maria Santos", "email": "maria@exemplo.com"},
                            {"id": "3", "name": "Pedro Oliveira", "email": "pedro@exemplo.com"}
                        ]
                    }
                }
                result = json.dumps(result_data, indent=2, ensure_ascii=False)
                self.finished.emit(result)
                
        except Exception as e:
            self.error.emit(str(e))


class QuerySyntaxHighlighter:
    """Highlighter básico para sintaxe GraphQL"""
    
    def __init__(self, text_edit):
        self.text_edit = text_edit
        self.keywords = ['query', 'mutation', 'subscription', 'fragment', 'on', 'true', 'false', 'null']
        self.types = ['ID', 'String', 'Int', 'Float', 'Boolean']
        
    def highlight(self):
        """Aplica highlighting básico"""
        cursor = self.text_edit.textCursor()
        cursor.select(cursor.SelectionType.Document)
        text = cursor.selection().toPlainText()
        
        # Cores
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # Azul para keywords
        
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#2E8B57"))  # Verde para tipos
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A52A2A"))  # Marrom para strings
        
        # Aplica formatação (simplificado)
        for keyword in self.keywords:
            self.highlight_word(keyword, keyword_format)
        
        for type_name in self.types:
            self.highlight_word(type_name, type_format)
    
    def highlight_word(self, word, format):
        """Highlight uma palavra específica"""
        cursor = self.text_edit.textCursor()
        text = self.text_edit.toPlainText()
        start = 0
        
        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(word), cursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(format)
            start = pos + len(word)


class GraphQLClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.query_history = []
        self.init_ui()
        self.setup_shortcuts()
        self.setup_syntax_highlighter()

    def init_ui(self):
        self.setWindowTitle('GraphQL Desktop Client')
        self.resize(1400, 800)

        # Fonte monoespaçada
        mono_font = QFont("Consolas", 10)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)

        # ==========================================
        # LAYOUT PRINCIPAL
        # ==========================================
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # ==========================================
        # 1. BARRA SUPERIOR (Autenticação e Ações)
        # ==========================================
        top_group = QGroupBox("Autenticação")
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        # Campo Org ID
        top_layout.addWidget(QLabel('Org ID:'))
        self.orgid_input = QLineEdit()
        self.orgid_input.setPlaceholderText('Digite o ID da organização...')
        self.orgid_input.setMaximumWidth(200)
        top_layout.addWidget(self.orgid_input)

        # Campo Token
        top_layout.addWidget(QLabel('Token:'))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('Digite seu token...')
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setMaximumWidth(300)
        top_layout.addWidget(self.token_input)

        # Checkbox para mostrar/ocultar token
        self.show_token_check = QCheckBox('Mostrar')
        self.show_token_check.stateChanged.connect(self.toggle_token_visibility)
        top_layout.addWidget(self.show_token_check)

        top_layout.addStretch()

        # Botões de Ação
        self.btn_introspect = QPushButton('🔍 Introspecção')
        self.btn_introspect.clicked.connect(self.run_introspection)
        self.btn_introspect.setMaximumWidth(150)
        top_layout.addWidget(self.btn_introspect)

        self.btn_execute = QPushButton('▶ Executar Query')
        self.btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_execute.clicked.connect(self.run_query)
        self.btn_execute.setMaximumWidth(150)
        top_layout.addWidget(self.btn_execute)

        self.btn_clear = QPushButton('🗑 Limpar')
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear.setMaximumWidth(100)
        top_layout.addWidget(self.btn_clear)

        top_group.setLayout(top_layout)
        main_layout.addWidget(top_group)

        # ==========================================
        # 2. ÁREA CENTRAL COM ABAS
        # ==========================================
        central_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Abas para Query e Variáveis
        query_tab_widget = QTabWidget()
        
        # Aba Query
        query_tab = QWidget()
        query_layout = QVBoxLayout()
        query_layout.setContentsMargins(0, 0, 0, 0)
        self.query_editor = QPlainTextEdit()
        self.query_editor.setFont(mono_font)
        self.query_editor.setPlaceholderText('Escreva sua query GraphQL aqui...\n\n{\n  users {\n    id\n    name\n    email\n  }\n}')
        query_layout.addWidget(self.query_editor)
        query_tab.setLayout(query_layout)
        query_tab_widget.addTab(query_tab, "Query")
        
        # Aba Variáveis
        variables_tab = QWidget()
        variables_layout = QVBoxLayout()
        variables_layout.setContentsMargins(0, 0, 0, 0)
        self.variables_editor = QPlainTextEdit()
        self.variables_editor.setFont(mono_font)
        self.variables_editor.setPlaceholderText('{\n  "userId": "123",\n  "limit": 10\n}')
        variables_layout.addWidget(self.variables_editor)
        variables_tab.setLayout(variables_layout)
        query_tab_widget.addTab(variables_tab, "Variáveis (JSON)")
        
        central_splitter.addWidget(query_tab_widget)

        # Coluna da Esquerda: Introspecção
        intro_group = QGroupBox("Schema (Introspecção)")
        intro_layout = QVBoxLayout()
        intro_layout.setContentsMargins(5, 5, 5, 5)
        self.intro_editor = QPlainTextEdit()
        self.intro_editor.setReadOnly(True)
        self.intro_editor.setFont(mono_font)
        self.intro_editor.setPlaceholderText('O schema aparecerá aqui...')
        intro_layout.addWidget(self.intro_editor)
        intro_group.setLayout(intro_layout)
        central_splitter.addWidget(intro_group)

        # Coluna da Direita: Resultados
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(5, 5, 5, 5)
        
        # Tabs para resultado e histórico
        result_tabs = QTabWidget()
        
        # Tab Resultado
        self.result_editor = QPlainTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setFont(mono_font)
        self.result_editor.setPlaceholderText('O resultado aparecerá aqui...')
        result_tabs.addTab(self.result_editor, "Resultado")
        
        # Tab Histórico
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_query_from_history)
        result_tabs.addTab(self.history_list, "Histórico")
        
        result_layout.addWidget(result_tabs)
        result_group.setLayout(result_layout)
        central_splitter.addWidget(result_group)

        # Define tamanhos iniciais
        central_splitter.setSizes([500, 300, 400])
        
        main_layout.addWidget(central_splitter)

        # ==========================================
        # 3. STATUS BAR (CORRIGIDO)
        # ==========================================
        self.status_bar = QStatusBar()
        self.status_bar.setMaximumHeight(25)  # Limita altura do status bar
        self.status_bar.showMessage('Pronto.')
        self.status_bar.setStyleSheet("QStatusBar { padding: 2px; border-top: 1px solid #ccc; }")
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)

    def setup_shortcuts(self):
        """Configura atalhos de teclado"""
        shortcut_execute = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_execute.activated.connect(self.run_query)
        
        shortcut_introspect = QShortcut(QKeySequence("Ctrl+I"), self)
        shortcut_introspect.activated.connect(self.run_introspection)
        
        shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save.activated.connect(self.save_query_to_history)

    def setup_syntax_highlighter(self):
        """Configura syntax highlighter"""
        self.highlighter = QuerySyntaxHighlighter(self.query_editor)
        self.query_editor.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        """Atualiza highlighting quando texto muda"""
        # self.highlighter.highlight()  # Pode ser pesado, usar com cautela

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
        reply = QMessageBox.question(self, 'Confirmar', 
                                     'Deseja limpar todos os campos?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.intro_editor.clear()
            self.query_editor.clear()
            self.variables_editor.clear()
            self.result_editor.clear()
            self.status_bar.showMessage('Tudo limpo.')

    def save_query_to_history(self):
        """Salva query atual no histórico"""
        query = self.query_editor.toPlainText().strip()
        if query:
            timestamp = datetime.now().strftime("%H:%M:%S")
            item = QListWidgetItem(f"[{timestamp}] {query[:50]}...")
            item.setData(Qt.ItemDataRole.UserRole, query)
            self.history_list.addItem(item)
            self.status_bar.showMessage('Query salva no histórico (Ctrl+S)')

    def load_query_from_history(self, item):
        """Carrega query do histórico"""
        query = item.data(Qt.ItemDataRole.UserRole)
        if query:
            self.query_editor.setPlainText(query)
            self.status_bar.showMessage('Query carregada do histórico')

    def run_introspection(self):
        """Executa a introspecção em thread separada"""
        creds = self.get_credentials()
        if not creds['orgid'] or not creds['token']:
            QMessageBox.warning(self, 'Atenção', 'Preencha o Org ID e o Token.')
            return

        self.status_bar.showMessage('Executando introspecção...')
        self.btn_introspect.setEnabled(False)
        
        self.worker = GraphQLWorker('introspect', creds['orgid'], creds['token'])
        self.worker.finished.connect(self.on_introspection_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def run_query(self):
        """Executa a query em thread separada"""
        creds = self.get_credentials()
        query = self.query_editor.toPlainText().strip()
        variables_text = self.variables_editor.toPlainText().strip()

        if not creds['orgid'] or not creds['token']:
            QMessageBox.warning(self, 'Atenção', 'Preencha o Org ID e o Token.')
            return
        
        if not query:
            QMessageBox.warning(self, 'Atenção', 'O campo de query está vazio.')
            return

        # Parse variables se houver
        variables = None
        if variables_text:
            try:
                variables = json.loads(variables_text)
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, 'Erro', f'Variáveis em formato JSON inválido:\n{e}')
                return

        self.status_bar.showMessage('Executando query...')
        self.btn_execute.setEnabled(False)
        
        self.worker = GraphQLWorker('query', creds['orgid'], creds['token'], query, variables)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_introspection_finished(self, result):
        """Callback quando introspecção termina"""
        self.intro_editor.setPlainText(result)
        self.status_bar.showMessage('Introspecção concluída.')
        self.btn_introspect.setEnabled(True)

    def on_query_finished(self, result):
        """Callback quando query termina"""
        self.result_editor.setPlainText(result)
        self.status_bar.showMessage('Query executada com sucesso.')
        self.btn_execute.setEnabled(True)
        
        # Adiciona ao histórico automaticamente
        query = self.query_editor.toPlainText().strip()
        if query and (not self.query_history or self.query_history[-1] != query):
            self.query_history.append(query)
            timestamp = datetime.now().strftime("%H:%M:%S")
            item = QListWidgetItem(f"[{timestamp}] {query[:50]}...")
            item.setData(Qt.ItemDataRole.UserRole, query)
            self.history_list.addItem(item)

    def on_error(self, error_msg):
        """Callback quando ocorre erro"""
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