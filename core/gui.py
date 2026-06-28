from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPlainTextEdit,
                             QPushButton, QSplitter, QStatusBar, QTabWidget, QVBoxLayout, QWidget)
from PyQt6.QtGui import QAction, QFont, QKeySequence, QShortcut

# classe para gerar a interface gráfica
class GraphQLClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.query_history = []
        self.init_ui()
        self.setup_shortcuts()
        self.create_menu_bar()

    def create_menu_bar(self):
        menubar = self.menuBar():
        menubar.setStyleSheet("QMenuBar { padding: 2px 5px; }")

        # Menu Arquivo
        file_menu = menubar.addMenu('&Arquivo')

        new_action = QAction('&Nova Query', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_query) # método de criar query
        file_menu.addAction(new_action)

        save_action = QAction('&Salvar Query', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_query_to_history) # método de salvar query para o histórico
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('&Sair', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Editar
        edit_menu = menubar.addMenu('&Editar')

        clear_action = QAction('&Limpar Tudo', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_action)

        edit_menu.addSeparator()

        copy_action = QAction('&Copiar Resultado', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy_result)
        edit_menu.addAction(copy_action)

        #Menu Ferramentas
        tools_menu = menubar.addMenu('&Ferramentas')

        introspect_action = QAction('&Introspecção', self)
        introspect_action.setShortcut('Ctrl+I')
        introspect_action.triggered.connect(self.run_introspection)
        tools_menu.addAction(introspect_action)

        #Menu Ajuda
        help_menu = menubar.addMenu('&Ajuda')

        about_action = QAction('&Sobre', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def init_ui(self):
        self.setWindowTitle('GraphQL Desktop Client')
        self.setGeometry(1400, 800)

        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(3, 3, 3, 3)

        # Barra de autenticação
        auth_layout = QHBoxLayout()
        auth_layout.setSpacing(8)
        auth_layout.setContentsMargins(5, 5, 5, 5)

        # Org ID
        auth_layout.addWidget(QLabel('<b>Org ID:</b>'))
        self.orgid_input = QLineEdit()
        self.orgid_input.setPlaceholderText('ID da organização')
        self.orgid_input.setMaximumWidth(180)
        self.orgid_input.setMinimumWidth(150)
        auth_layout.addWidget(self.orgid_input)

        # Token
        auth_layout.addWidget(QLabel('<b>Token:</b>'))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('Token de autenticação')
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setMaximumWidth(300)
        self.token_input.setMinimumWidth(250)
        auth_layout.addWidget(self.token_input)

        # Checkbox mostrar token
        self.show_token_checkbox = QCheckBox('Mostrar')
        self.show_token_check.stateChanged.connect(self.toggle_token_visibility)
        auth_layout.addWidget(self.show_token_checkbox)

        auth_layout.addStretch()

        # Botões compactos
        self.btn_introspect = QPushButton('Introspecção')
        self.btn_introspect.setMaximumWidth(120)
        self.btn_introspect.clicked.connect(self.run_introspection)
        auth_layout.addWidget(self.btn_introspect)

        self.btn_execute = QPushButton('Executar Query')
        self.btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_execute.setMaximumWidth(100)
        self.btn_execute.clicked.connect(self.run_query)
        auth_layout.addWidget(self.btn_execute)

        self.btn_clear = QPushButton('🗑 Limpar')
        self.btn_clear.setMaximumWidth(80)
        self.btn_clear.clicked.connect(self.clear_all)
        auth_layout.addWidget(self.btn_clear)

        main_layout.addLayout(auth_layout)

        # Área Central
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Coluna 1: Introspecção
        intro_widget = QWidget()
        intro_layout = QVBoxLayout(intro_widget)
        intro_layout.setContentsMargins(5, 5, 5, 5)

        self.intro_label = QLabel('<b>Schema (Introspecção):</b>')
        intro_layout.addWidget(self.intro_label)

        self.intro_editor = QPlainTextEdit()
        self.intro_editor.setReadOnly(True)
        self.intro_editor.setFont(QFont('Consolas', 10))
        self.intro_editor.setPlaceholderText('O schema aparecerá aqui...')
        intro_layout.addWidget(self.intro_editor)

        self.splitter.addWidget(intro_widget)

        # Coluna 2: Query e Variáveis
        query_widget = QWidget()
        query_layout = QVBoxLayout(query_widget)
        query_layout.setContentsMargins(0, 0, 0, 0)

        self.query_tabs = QTabWidget()
        
        # Aba de query
        self.query_editor = QPlainTextEdit()
        self.query_editor.setFont(QFont('Consolas', 10))
        self.query_editor.setPlaceholderText('Digite sua query GraphQL aqui...')
        self.query_tabs.addTab(self.query_editor, 'Query')

        # Aba de variáveis
        self.variables_editor = QPlainTextEdit()
        self.variables_editor.setFont(QFont('Consolas', 10))
        self.variables_editor.setPlaceholderText('{\n  "userId": "123",\n  "limit": 10\n}')
        self.query_tabs.addTab(self.variables_editor, 'Variáveis (JSON)')

        query_layout.addWidget(self.query_tabs)
        self.splitter.addWidget(query_widget)

        # Coluna 3: Resultados
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(0, 0, 0, 0)

        self.result_tabs = QTabWidget()

        # Aba de resultados
        self.result_editor = QPlainTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setFont(QFont('Consolas', 10))
        self.result_editor.setPlaceholderText('O resultado da query aparecerá aqui...')
        self.result_tabs.addTab(self.result_editor, 'Resultado')

        # Aba de histórico
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_query_from_history)
        self.result_tabs.addTab(self.history_list, 'Histórico')

        result_layout.addWidget(self.result_tabs)
        self.splitter.addWidget(result_widget)

        # Tamanhos iniciais das colunas
        self.splitter.setSizes([400, 400, 400])

        main_layout.addWidget(self.splitter)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setMaximumHeight(22)
        self.status_bar.showMessage('Pronto')
        self.setStatusBar(self.status_bar)

    def setup_shortcuts(self):
        # Executar query
        shortcut_execute = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_execute.activated.connect(self.run_query)

        # Introspecção
        shortcut_introspect = QShortcut(QKeySequence("Ctrl+I"), self)
        shortcut_introspect.activated.connect(self.run_introspection)

        # Salvar no histórico
        shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save.activated.connect(self.save_query_to_history)

        # Nova query
        shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new.activated.connect(self.new_query)

        # Limpar
        shortcut_clear = QShortcut(QKeySequence("Ctrl+L"), self)
        shortcut_clear.activated.connect(self.clear_all)

    def toggle_token_visibility(self, state):
        pass