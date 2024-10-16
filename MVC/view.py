from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit,
    QLabel, QTreeWidget, QTreeWidgetItem, QProgressBar, QStatusBar, QMenu
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QPoint
import logging

class FileStructureView(QWidget):
    """
    Interface gráfica para criar e visualizar a estrutura de arquivos.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Structure Creator")
        self.setGeometry(100, 100, 900, 700)
        self.selected_directory = ""
        self.init_ui()

    def init_ui(self):
        """
        Inicializa a interface gráfica do usuário (UI).
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Label informativo
        info_label = QLabel("Indentação: 4 espaços | Símbolos de hierarquia: ├──, └──, │")
        main_layout.addWidget(info_label)

        # Seção para seleção de diretório
        dir_layout = QHBoxLayout()
        self.dir_button = QPushButton("Selecionar Diretório de Destino")
        dir_layout.addWidget(self.dir_button)

        self.dir_label = QLabel("Nenhum diretório selecionado.")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        main_layout.addLayout(dir_layout)

        # Editor de texto para inserir a estrutura
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Cole aqui a estrutura de arquivos e pastas...")
        font = QFont("Consolas", 10)
        self.text_edit.setFont(font)
        main_layout.addWidget(self.text_edit)

        # Widget para exibir a árvore de diretórios/arquivos
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)  # Esconder o cabeçalho da árvore
        self.tree_widget.setIndentation(20)     # Definir indentação
        self.tree_widget.setAnimated(True)      # Habilitar animação para expandir/colapsar
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.open_context_menu)
        main_layout.addWidget(self.tree_widget)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Progresso: %p%")
        main_layout.addWidget(self.progress_bar)

        # Barra de status
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        # Botões de ação
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Criar Estrutura de Arquivos")
        self.create_button.setEnabled(False)
        button_layout.addWidget(self.create_button)

        # Adicionando botões para Expandir e Colapsar Tudo
        self.expand_all_button = QPushButton("Expandir Tudo")
        self.collapse_all_button = QPushButton("Colapsar Tudo")
        button_layout.addWidget(self.expand_all_button)
        button_layout.addWidget(self.collapse_all_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def clear_tree(self):
        """
        Limpa a visualização da árvore de arquivos.
        """
        self.tree_widget.clear()

    def add_item_to_tree(self, node, parent_item=None):
        """
        Adiciona itens à árvore de visualização.

        Args:
            - node: Instância da classe Node representando o arquivo ou diretório.
            - parent_item: O item pai na árvore, se houver.
        """
        tree_item = QTreeWidgetItem([node.name])
        if node.is_dir:
            tree_item.setIcon(0, QIcon.fromTheme("folder"))
        else:
            tree_item.setIcon(0, QIcon.fromTheme("text-x-generic"))

        if parent_item:
            parent_item.addChild(tree_item)
        else:
            self.tree_widget.addTopLevelItem(tree_item)

        logging.info(f"Adicionando item: {node.name} (diretório: {node.is_dir})")

        if node.is_dir and node.children:
            for child in node.children:
                self.add_item_to_tree(child, tree_item)

    def open_context_menu(self, position: QPoint):
        """
        Abre um menu de contexto ao clicar com o botão direito do mouse na árvore.

        Args:
            - position: Posição onde o menu de contexto deve ser aberto.
        """
        selected_item = self.tree_widget.itemAt(position)
        if selected_item:
            menu = QMenu()
            expand_action = menu.addAction("Expandir")
            collapse_action = menu.addAction("Colapsar")
            action = menu.exec(self.tree_widget.mapToGlobal(position))
            if action == expand_action:
                selected_item.setExpanded(True)
            elif action == collapse_action:
                selected_item.setExpanded(False)
