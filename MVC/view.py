from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QLabel, QTreeWidget, QTreeWidgetItem, QProgressBar, QStatusBar, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QIcon
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

        info_label = QLabel("Indentação: 4 espaços | Símbolos de hierarquia: ├──, └──, │")
        main_layout.addWidget(info_label)

        dir_layout = QHBoxLayout()
        self.dir_button = QPushButton("Selecionar Diretório de Destino")
        dir_layout.addWidget(self.dir_button)

        self.dir_label = QLabel("Nenhum diretório selecionado.")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        main_layout.addLayout(dir_layout)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Cole aqui a estrutura de arquivos e pastas...")
        font = QFont("Consolas", 10)
        self.text_edit.setFont(font)
        main_layout.addWidget(self.text_edit)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(20)
        self.tree_widget.setAnimated(True)
        main_layout.addWidget(self.tree_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Progresso: %p%")
        main_layout.addWidget(self.progress_bar)

        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Criar Estrutura de Arquivos")
        self.create_button.setEnabled(False)
        button_layout.addWidget(self.create_button)
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
