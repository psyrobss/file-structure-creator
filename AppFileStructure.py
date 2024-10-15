import sys
import os
import re
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QFileDialog,
    QLabel,
    QMessageBox,
    QStatusBar,
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileStructureCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Structure Creator")
        self.setGeometry(100, 100, 900, 700)
        self.selected_directory = ""
        self.init_ui()  # Inicializa a interface do usuário

    def init_ui(self):
        # Layout principal vertical
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Layout horizontal para o botão de seleção de diretório e label
        dir_layout = QHBoxLayout()
        self.dir_button = QPushButton("Select Destination Directory")
        icon = QIcon.fromTheme("folder")
        if icon.isNull():
            icon = QIcon("fallback_folder_icon.png")
        self.dir_button.setIcon(icon)
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_button)

        self.dir_label = QLabel("No directory selected.")
        self.dir_label.setStyleSheet("font-weight: bold;")
        dir_layout.addWidget(self.dir_label)

        dir_layout.addStretch()
        main_layout.addLayout(dir_layout)

        # Editor de texto para colar a estrutura
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Paste the file and folder structure here, for example:\n"
            "Folder/\n"
            "├── file.txt\n"
            "└── subfolder/\n"
            "    └── file2.txt\n"
            "Or:\n"
            "Folder/\n"
            "+-- file.txt\n"
            "+-- subfolder/\n"
            "    +-- file2.txt\n"
        )
        font = QFont("Consolas", 11)
        self.text_edit.setFont(font)
        self.text_edit.textChanged.connect(self.validate_structure)
        main_layout.addWidget(self.text_edit)

        # Label para exibir mensagens de erro
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.error_label)

        # Layout horizontal para o botão de criação da estrutura
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create File Structure")
        self.create_button.setIcon(QIcon.fromTheme("document-save"))
        self.create_button.clicked.connect(self.create_structure)
        self.create_button.setEnabled(False)
        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Barra de status para fornecer feedback contínuo
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)

        # Aplicar estilos personalizados
        self.apply_styles()

    def apply_styles(self):
        # Estilos CSS personalizados para os widgets
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
        """)

    def select_directory(self):
        # Abre um diálogo para selecionar o diretório de destino
        directory = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory", os.getcwd()
        )
        if directory:
            self.selected_directory = directory
            self.dir_label.setText(f"Selected Directory: {self.selected_directory}")
            self.status_bar.showMessage(f"Selected directory: {self.selected_directory}")
        else:
            self.dir_label.setText("No directory selected.")
            self.status_bar.showMessage("No directory selected.")

    def validate_structure(self):
        # Valida a estrutura de arquivos e pastas inserida pelo usuário
        structure_text = self.text_edit.toPlainText()
        if not structure_text.strip():
            self.error_label.setText("The structure is empty.")
            self.create_button.setEnabled(False)
            self.status_bar.showMessage("The structure is empty.")
            return

        try:
            self.parsed_structure = self.parse_structure(structure_text)
            self.error_label.setText("")
            self.create_button.setEnabled(True)
            self.status_bar.showMessage("Valid structure.")
        except ValueError as ve:
            self.error_label.setText(str(ve))
            self.create_button.setEnabled(False)
            self.status_bar.showMessage("Invalid structure.")

    def parse_structure(self, text):
        """
        Analisa a estrutura de arquivos e pastas e retorna uma lista de tuplas
        contendo (nível, nome, é_diretório).
        """
        lines = text.splitlines()
        parsed_lines = []
        indent_pattern = re.compile(r'^( *)')  # Captura espaços no início da linha

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Remove caracteres de desenho da árvore
            line_no_tree = re.sub(r'[├└─│]+', '', line)

            # Captura a indentação
            indent_match = indent_pattern.match(line_no_tree)
            indent = indent_match.group(1)
            level = len(indent) // 4  # Assume 4 espaços por nível de indentação

            # Obtém o nome do arquivo/pasta
            name = line_no_tree.strip()

            if not name:
                raise ValueError(f"Line {idx}: File or directory name is empty.")

            # Verifica se é um diretório
            is_dir = name.endswith('/')
            if is_dir:
                name = name.rstrip('/')

            parsed_lines.append((level, name, is_dir))

        return parsed_lines

    def create_structure(self):
        # Cria a estrutura de arquivos e pastas com base na entrada
        if not self.selected_directory:
            QMessageBox.warning(self, "No Directory Selected", "Please select a destination directory.")
            return

        try:
            stack = []
            for level, name, is_dir in self.parsed_structure:
                # Ajusta a pilha de diretórios
                while len(stack) > level:
                    stack.pop()

                stack.append(name)

                # Define o caminho completo
                path = os.path.join(self.selected_directory, *stack)

                if is_dir:
                    if not os.path.exists(path):
                        os.makedirs(path)
                    self.log_message(f"Directory created: {path}")
                else:
                    dir_name = os.path.dirname(path)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                    with open(path, 'w', encoding='utf-8') as f:
                        pass  # Cria um arquivo vazio
                    self.log_message(f"File created: {path}")

            QMessageBox.information(self, "Success", "File and folder structure created successfully!")
            self.status_bar.showMessage("Structure created successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while creating the structure:\n{str(e)}")
            self.status_bar.showMessage("Error creating the structure.")

    def log_message(self, message):
        # Loga mensagens tanto no console quanto na barra de status
        logging.info(message)
        self.status_bar.showMessage(message)

def main():
    # Ponto de entrada da aplicação
    app = QApplication(sys.argv)
    window = FileStructureCreator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
