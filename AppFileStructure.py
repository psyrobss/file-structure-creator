import sys
import os
import re
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QPlainTextEdit, QFileDialog, QLabel, QMessageBox, QStatusBar,
    QComboBox, QTreeWidget, QTreeWidgetItem, QProgressBar
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# Configuração básica do logging para exibir mensagens no console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileStructureCreator(QWidget):
    INVALID_CHARACTERS = r'<>:"|?*'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Structure Creator")
        self.setGeometry(100, 100, 900, 700)
        self.selected_directory = ""
        self.parsed_structure = []  # Armazena a estrutura analisada
        self.base_path = None  # Caminho da pasta raiz
        self.expected_indent = 4
        self.indent_str = '    '
        self.hier_symbols = {
            'branch': '├── ',
            'last_branch': '└── ',
            'vertical': '│   ',
            'none': '    '
        }
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Configuração de indentação e símbolos
        config_layout = QHBoxLayout()
        self.indent_label = QLabel("Tipo de Indentação:")
        config_layout.addWidget(self.indent_label)

        self.indent_combo = QComboBox()
        self.indent_combo.addItems(["4 Espaços", "Tab"])
        self.indent_combo.currentIndexChanged.connect(self.update_parser_settings)
        config_layout.addWidget(self.indent_combo)

        self.symbol_label = QLabel("Símbolos de Hierarquia:")
        config_layout.addWidget(self.symbol_label)

        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["Padrão (├──, └──, │)", "Simplificado (+--, |)"])
        self.symbol_combo.currentIndexChanged.connect(self.update_parser_settings)
        config_layout.addWidget(self.symbol_combo)

        config_layout.addStretch()
        main_layout.addLayout(config_layout)

        # Seleção de diretório
        dir_layout = QHBoxLayout()
        self.dir_button = QPushButton("Selecionar Diretório de Destino")
        icon = QIcon.fromTheme("folder")
        if icon.isNull():
            icon = QIcon("fallback_folder_icon.png")
        self.dir_button.setIcon(icon)
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_button)

        self.dir_label = QLabel("Nenhum diretório selecionado.")
        self.dir_label.setStyleSheet("font-weight: bold;")
        dir_layout.addWidget(self.dir_label)
        dir_layout.addStretch()
        main_layout.addLayout(dir_layout)

        # Editor de texto para estrutura
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Cole a estrutura de arquivos e pastas aqui...")
        font = QFont("Consolas", 11)
        self.text_edit.setFont(font)
        self.text_edit.textChanged.connect(self.validate_structure)
        main_layout.addWidget(self.text_edit)

        # Pré-visualização com QTreeWidget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        main_layout.addWidget(self.tree_widget)

        # Label de erros
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.error_label)

        # Botão de criação da estrutura
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Criar Estrutura de Arquivos")
        self.create_button.clicked.connect(self.create_structure)
        self.create_button.setEnabled(False)
        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Progresso: %p%")
        main_layout.addWidget(self.progress_bar)

        # Barra de status
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Pronto")
        main_layout.addWidget(self.status_bar)

        # Aplicar estilos
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
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
            }
            QLabel {
                font-size: 14px;
            }
            QProgressBar {
                text-align: center;
            }
        """)

    def update_parser_settings(self):
        indent_type = self.indent_combo.currentText()
        if indent_type == "4 Espaços":
            self.expected_indent = 4
            self.indent_str = '    '
        elif indent_type == "Tab":
            self.expected_indent = 1
            self.indent_str = '\t'

        symbol_set = self.symbol_combo.currentText()
        if symbol_set == "Padrão (├──, └──, │)":
            self.hier_symbols = {
                'branch': '├── ',
                'last_branch': '└── ',
                'vertical': '│   ',
                'none': '    '
            }
        elif symbol_set == "Simplificado (+--, |)":
            self.hier_symbols = {
                'branch': '+-- ',
                'last_branch': '+-- ',
                'vertical': '|   ',
                'none': '    '
            }
        self.validate_structure()

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
        previous_level = -1

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Remover todos os símbolos da árvore do início da linha
            line_no_tree = re.sub(r'^[\│\├\└\─\+]+', '', line).strip()

            # Captura a indentação e o nome
            pattern = r'^(?P<indent>(?:\s*)*)(?P<name>.+)$'
            m = re.match(pattern, line_no_tree)

            if m:
                indent = m.group('indent')
                name = m.group('name').strip()

                # Calcula o nível de indentação
                spaces = len(indent)
                if spaces % self.expected_indent != 0:
                    raise ValueError(f"Linha {idx}: Indentação inconsistente. Use {self.expected_indent} espaços por nível.")

                level = spaces // self.expected_indent
                if level > previous_level + 1:
                    raise ValueError(f"Linha {idx}: Indentação incorreta.")

                previous_level = level

                # Verifica se o nome do arquivo ou diretório é válido
                if not name:
                    raise ValueError(f"Linha {idx}: O nome do arquivo ou diretório está vazio.")

                # Verifica se é um diretório
                is_dir = name.endswith('/')
                if is_dir:
                    name = name.rstrip('/')

                parsed_lines.append((level, name, is_dir))
            else:
                raise ValueError(f"Linha {idx}: Não foi possível analisar a linha.")

        return parsed_lines

    def update_tree_preview(self):
        self.tree_widget.clear()
        root_items = {}
        for level, name, is_dir in self.parsed_structure:
            item = QTreeWidgetItem([name + ('/' if is_dir else '')])
            if level == 0:
                self.tree_widget.addTopLevelItem(item)
                root_items[level] = item
            else:
                parent = root_items.get(level - 1)
                if parent:
                    parent.addChild(item)
                    if is_dir:
                        root_items[level] = item
        self.tree_widget.expandAll()

    def create_structure(self):
        if not self.selected_directory:
            QMessageBox.warning(self, "Nenhum Diretório Selecionado", "Por favor, selecione um diretório de destino.")
            return

        try:
            stack = []
            self.base_path = None  # Caminho da pasta raiz
            total_items = len(self.parsed_structure)
            created_items = 0
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(total_items)

            for idx, (level, name, is_dir) in enumerate(self.parsed_structure):
                while len(stack) > level:
                    stack.pop()

                if idx == 0:
                    if not is_dir:
                        raise Exception("O primeiro item deve ser um diretório raiz.")
                    self.base_path = os.path.join(self.selected_directory, name)
                    stack.append(name)
                    if not os.path.exists(self.base_path):
                        os.makedirs(self.base_path)
                        self.log_message(f"Diretório raiz criado: {self.base_path}")
                    else:
                        self.log_message(f"Diretório raiz já existe: {self.base_path}")
                    created_items += 1
                    self.progress_bar.setValue(created_items)
                    continue

                current_path = os.path.join(self.base_path, *stack[1:], name)

                if is_dir:
                    stack.append(name)
                    if not os.path.exists(current_path):
                        os.makedirs(current_path)
                        self.log_message(f"Diretório criado: {current_path}")
                else:
                    dir_name = os.path.dirname(current_path)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                        self.log_message(f"Diretório criado para o arquivo: {dir_name}")
                    with open(current_path, 'w', encoding='utf-8') as f:
                        pass  # Cria um arquivo vazio
                    self.log_message(f"Arquivo criado: {current_path}")

                created_items += 1
                self.progress_bar.setValue(created_items)

            QMessageBox.information(self, "Sucesso", "Estrutura de arquivos criada com sucesso!")
            self.status_bar.showMessage("Estrutura criada com sucesso.")
            self.progress_bar.setValue(total_items)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar a estrutura: {str(e)}")
            self.progress_bar.setValue(0)

    def log_message(self, message):
        """
        Exibe a mensagem no console e na barra de status da interface.
        """
        logging.info(message)  # Exibe no console
        self.status_bar.showMessage(message)  # Exibe na barra de status

def main():
    app = QApplication(sys.argv)
    window = FileStructureCreator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
