import sys
import os
import re
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QPlainTextEdit, QFileDialog, QLabel, QMessageBox, QStatusBar,
    QTreeWidget, QTreeWidgetItem, QProgressBar, QHeaderView
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HierarchicalItem:
    """
    Classe que representa um item hierárquico (diretório ou arquivo).
    """
    def __init__(self, level, name, is_dir):
        self.level = level
        self.name = name
        self.is_dir = is_dir

    def __repr__(self):
        tipo = "Diretório" if self.is_dir else "Arquivo"
        return f"{' ' * (self.level * 4)}{self.name} ({tipo})"

    def get_full_path(self, parent_path):
        return os.path.join(parent_path, self.name)

    def is_root(self):
        return self.level == 0

class FileStructureCreator(QWidget):
    INVALID_CHARACTERS = r'<>:"|?*'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Structure Creator")
        self.setGeometry(100, 100, 900, 700)
        self.selected_directory = ""
        self.parsed_structure = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        info_label = QLabel("Indentação: 4 espaços | Símbolos de hierarquia: ├──, └──, │")
        main_layout.addWidget(info_label)

        dir_layout = QHBoxLayout()
        self.dir_button = QPushButton("Selecionar Diretório de Destino")
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_button)

        self.dir_label = QLabel("Nenhum diretório selecionado.")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        main_layout.addLayout(dir_layout)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Cole aqui a estrutura de arquivos e pastas...")
        font = QFont("Consolas", 10)
        self.text_edit.setFont(font)
        self.text_edit.textChanged.connect(self.validate_structure)
        main_layout.addWidget(self.text_edit)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(20)
        self.tree_widget.setAnimated(True)
        self.tree_widget.setColumnCount(1)
        main_layout.addWidget(self.tree_widget)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 10px;")
        main_layout.addWidget(self.error_label)

        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Criar Estrutura de Arquivos")
        self.create_button.clicked.connect(self.create_structure)
        self.create_button.setEnabled(False)
        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Progresso: %p%")
        main_layout.addWidget(self.progress_bar)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Pronto")
        main_layout.addWidget(self.status_bar)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #a5d6a7;
            }
            QPushButton:hover:!disabled {
                background-color: #45a049;
            }
            QPlainTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-family: Consolas;
                font-size: 12px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QProgressBar {
                text-align: center;
                font-size: 12px;
                color: black;
                background-color: #e0e0e0;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 4px;
                font-size: 10px;
            }
        """)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Destino", os.getcwd())
        if directory:
            self.selected_directory = directory
            self.dir_label.setText(f"Diretório Selecionado: {self.selected_directory}")
            self.status_bar.showMessage(f"Diretório selecionado: {self.selected_directory}")

    def validate_structure(self):
        structure_text = self.text_edit.toPlainText()
        if not structure_text.strip():
            self.error_label.setText("A estrutura está vazia.")
            self.create_button.setEnabled(False)
            self.tree_widget.clear()
            return

        try:
            self.parsed_structure = self.parse_structure(structure_text)
            self.error_label.setText("")
            self.create_button.setEnabled(True)
            self.status_bar.showMessage("Estrutura válida.")
            self.update_tree_preview()
        except ValueError as ve:
            self.error_label.setText(str(ve))
            self.create_button.setEnabled(False)
            self.tree_widget.clear()

    def parse_structure(self, text):
        lines = text.splitlines()
        parsed_lines = []
        indent_pattern = re.compile(r'^( *)')

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            line_no_tree = re.sub(r'[├└─│]+', '', line)
            indent_match = indent_pattern.match(line_no_tree)
            indent = indent_match.group(1) if indent_match else ''
            level = len(indent) // 4

            name = line_no_tree.strip()
            if not name:
                raise ValueError(f"Linha {idx}: Nome do arquivo ou diretório está vazio.")

            is_dir = name.endswith('/')
            if is_dir:
                name = name.rstrip('/')

            item = HierarchicalItem(level, name, is_dir)
            parsed_lines.append(item)

        return parsed_lines

    def update_tree_preview(self):
        self.tree_widget.clear()
        root_items = {}

        folder_icon = QIcon.fromTheme("folder")
        file_icon = QIcon.fromTheme("text-x-generic")

        for item in self.parsed_structure:
            tree_item = QTreeWidgetItem([item.name + ('/' if item.is_dir else '')])
            if item.is_dir:
                tree_item.setIcon(0, folder_icon)
            else:
                tree_item.setIcon(0, file_icon)

            if item.is_root():
                self.tree_widget.addTopLevelItem(tree_item)
                root_items[item.level] = tree_item
            else:
                parent = root_items.get(item.level - 1)
                if parent:
                    parent.addChild(tree_item)
                    if item.is_dir:
                        root_items[item.level] = tree_item

        self.tree_widget.expandAll()

    def create_structure(self):
        if not self.selected_directory:
            QMessageBox.warning(self, "Nenhum Diretório Selecionado", "Por favor, selecione um diretório de destino.")
            return

        try:
            stack = []
            root_dir = "code_creator_app"

            base_path = os.path.join(self.selected_directory, root_dir)
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            self.log_message(f"Diretório raiz criado: {base_path}")

            for item in self.parsed_structure:
                while len(stack) > item.level:
                    stack.pop()

                parent_path = os.path.join(base_path, *stack)
                full_path = item.get_full_path(parent_path)

                if item.is_dir:
                    if not os.path.exists(full_path):
                        os.makedirs(full_path)
                    stack.append(item.name)
                    self.log_message(f"Diretório criado: {full_path}")
                else:
                    dir_name = os.path.dirname(full_path)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        pass
                    self.log_message(f"Arquivo criado: {full_path}")

            QMessageBox.information(self, "Sucesso", "Estrutura de arquivos criada com sucesso!")
            self.status_bar.showMessage("Estrutura criada com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar a estrutura: {str(e)}")

    def log_message(self, message):
        logging.info(message)
        self.status_bar.showMessage(message)

def main():
    app = QApplication(sys.argv)
    window = FileStructureCreator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
