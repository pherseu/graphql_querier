from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QAction

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