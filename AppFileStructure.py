import sys
import os
import re
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


class FileStructureCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Criador de Estrutura de Arquivos")
        self.setGeometry(100, 100, 900, 700)
        # Remova ou comente a linha abaixo se não tiver um ícone
        # self.setWindowIcon(QIcon('icon.png'))  # Opcional: Adicione um ícone ao seu aplicativo
        self.selected_directory = ""
        self.init_ui()

    def init_ui(self):
        """
        Inicializa a interface do usuário, configurando layouts, widgets e conexões de sinais.
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Layout horizontal para o botão de seleção de diretório e label
        dir_layout = QHBoxLayout()
        self.dir_button = QPushButton("Selecionar Diretório de Destino")
        self.dir_button.setIcon(QIcon.fromTheme("folder"))
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_button)

        self.dir_label = QLabel("Nenhum diretório selecionado.")
        self.dir_label.setStyleSheet("font-weight: bold;")
        dir_layout.addWidget(self.dir_label)

        dir_layout.addStretch()
        main_layout.addLayout(dir_layout)

        # Editor de texto para colar a estrutura
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Cole aqui a estrutura de arquivos e pastas, por exemplo:\n"
            "Pasta/\n"
            "├── Pasta/\n"
            "│   ├── Pasta/\n"
            "│   │   ├── Arquivo.js\n"
            "│   │   ├── Arquivo.js\n"
            "│   │   └── Arquivo.js\n"
            "│   ├── Pasta/\n"
            "│   │   ├── Arquivo.js\n"
            "│   │   ├── Arquivo.js\n"
            "│   │   ├── Arquivo.js\n"
            "│   │   └── Arquivo.js\n"
            "│   ├── Pasta/\n"
            "│   │   ├── Arquivo.js\n"
            "│   │   └── Arquivo.js\n"
            "│   ├── Pasta/\n"
            "│   │   └── Arquivo.js\n"
            "│   └── Arquivo.js\n"
            "├── Pasta/\n"
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
        self.create_button = QPushButton("Criar Estrutura de Arquivos")
        self.create_button.setIcon(QIcon.fromTheme("document-save"))
        self.create_button.clicked.connect(self.create_structure)
        self.create_button.setEnabled(False)  # Desativado até que a estrutura seja válida
        button_layout.addWidget(self.create_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Barra de status para fornecer feedback contínuo
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Pronto")
        main_layout.addWidget(self.status_bar)

        # Aplicar estilos personalizados
        self.apply_styles()

    def apply_styles(self):
        """
        Aplica estilos CSS personalizados para melhorar a aparência da interface.
        """
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
        """
        Abre um diálogo para o usuário selecionar o diretório de destino onde a estrutura será criada.
        Atualiza o label e a barra de status com o caminho selecionado.
        """
        directory = QFileDialog.getExistingDirectory(
            self, "Selecione o Diretório de Destino", os.getcwd()
        )
        if directory:
            self.selected_directory = directory
            self.dir_label.setText(f"Diretório Selecionado: {self.selected_directory}")
            self.status_bar.showMessage(f"Diretório selecionado: {self.selected_directory}")
        else:
            self.dir_label.setText("Nenhum diretório selecionado.")
            self.status_bar.showMessage("Nenhum diretório selecionado.")

    def validate_structure(self):
        """
        Valida a estrutura de diretórios e arquivos inserida pelo usuário.
        Habilita o botão de criação se a estrutura for válida, ou exibe mensagens de erro caso contrário.
        """
        structure_text = self.text_edit.toPlainText()
        if not structure_text.strip():
            self.error_label.setText("A estrutura está vazia.")
            self.create_button.setEnabled(False)
            self.status_bar.showMessage("A estrutura está vazia.")
            return

        try:
            self.parse_structure(structure_text)
            self.error_label.setText("")
            self.create_button.setEnabled(True)
            self.status_bar.showMessage("Estrutura válida.")
        except ValueError as ve:
            self.error_label.setText(str(ve))
            self.create_button.setEnabled(False)
            self.status_bar.showMessage("Estrutura inválida.")

    def parse_structure(self, text):
        """
        Analisa a estrutura de texto para validar a hierarquia de diretórios e arquivos.
        Lança uma exceção ValueError com uma mensagem específica se a estrutura for inválida.
        """
        lines = text.splitlines()
        stack = []
        previous_level = 0

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue  # Ignora linhas vazias

            # Calcula o nível de indentação baseado em espaços ou tabulações
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1)
            # Considera 4 espaços ou 1 tabulação por nível
            spaces = indent.count('    ')
            tabs = indent.count('\t')
            level = spaces + tabs

            # Remove os caracteres especiais como ├── ou └──
            name = re.sub(r'^[├└]──\s*', '', line.strip())

            if not name:
                raise ValueError(f"Linha {idx}: Nome do arquivo ou diretório está vazio.")

            # Verifica se é um diretório (termina com '/')
            is_dir = False
            if name.endswith('/'):
                is_dir = True
                name = name.rstrip('/')

            # Valida o nível de indentação (não pode pular níveis)
            if level > previous_level + 1:
                raise ValueError(f"Linha {idx}: Indentação inválida. Não pode pular níveis.")

            previous_level = level

            # Gerenciamento da pilha para manter a hierarquia
            if level > len(stack):
                if level == len(stack) + 1:
                    stack.append(name)
                else:
                    raise ValueError(f"Linha {idx}: Indentação inválida.")
            elif level == len(stack):
                if stack:
                    stack.pop()
                stack.append(name)
            else:
                # level < len(stack)
                for _ in range(len(stack) - level):
                    if stack:
                        stack.pop()
                    else:
                        raise ValueError(f"Linha {idx}: Estrutura de diretórios inconsistente.")
                if stack:
                    stack.pop()
                stack.append(name)

        # Se nenhuma exceção foi levantada, a estrutura é considerada válida

    def create_structure(self):
        """
        Cria a estrutura de diretórios e arquivos no diretório selecionado com base na estrutura inserida pelo usuário.
        Se um arquivo ou diretório já existir, adiciona um sufixo numérico para evitar duplicatas.
        """
        if not self.selected_directory:
            QMessageBox.warning(self, "Diretório Não Selecionado", "Por favor, selecione um diretório de destino.")
            return

        structure_text = self.text_edit.toPlainText()
        try:
            lines = structure_text.splitlines()
            stack = []  # Para manter o caminho atual baseado na indentação

            for line in lines:
                if not line.strip():
                    continue  # Ignora linhas vazias

                # Calcula o nível de indentação baseado em espaços ou tabulações
                indent_match = re.match(r'^(\s*)', line)
                indent = indent_match.group(1)
                spaces = indent.count('    ')
                tabs = indent.count('\t')
                level = spaces + tabs  # 4 espaços ou 1 tab por nível

                # Remove os caracteres especiais como ├── ou └──
                name = re.sub(r'^[├└]──\s*', '', line.strip())

                if not name:
                    continue  # Já validado anteriormente

                # Verifica se é um diretório (termina com '/')
                is_dir = False
                if name.endswith('/'):
                    is_dir = True
                    name = name.rstrip('/')

                # Atualiza o stack com base no nível atual
                if level > len(stack):
                    if level == len(stack) + 1:
                        stack.append(name)
                    else:
                        raise ValueError("Indentação inválida durante a criação.")
                elif level == len(stack):
                    if stack:
                        stack.pop()
                    stack.append(name)
                else:
                    # level < len(stack)
                    for _ in range(len(stack) - level):
                        if stack:
                            stack.pop()
                        else:
                            break
                    if stack:
                        stack.pop()
                    stack.append(name)

                # Cria o caminho completo
                path = os.path.join(self.selected_directory, *stack)

                # Garante que o nome seja único
                unique_path = self.get_unique_path(path, is_dir)

                if is_dir:
                    # É um diretório
                    os.makedirs(unique_path, exist_ok=True)
                else:
                    # É um arquivo, garante que o diretório exista
                    os.makedirs(os.path.dirname(unique_path), exist_ok=True)
                    # Cria o arquivo vazio
                    with open(unique_path, 'w', encoding='utf-8') as f:
                        pass  # Cria um arquivo vazio

            QMessageBox.information(self, "Sucesso", "Estrutura de arquivos e pastas criada com sucesso!")
            self.status_bar.showMessage("Estrutura criada com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao criar a estrutura:\n{str(e)}")
            self.status_bar.showMessage("Erro ao criar a estrutura.")

    def get_unique_path(self, path, is_dir):
        """
        Gera um caminho único adicionando um sufixo numérico se o caminho já existir.

        Args:
            path (str): Caminho original.
            is_dir (bool): Indica se o caminho é um diretório.

        Returns:
            str: Caminho único.
        """
        if not os.path.exists(path):
            return path

        base, ext = os.path.splitext(path) if not is_dir else (path, '')
        counter = 1

        while True:
            if is_dir:
                new_path = f"{base}{counter:02d}/"
            else:
                new_path = f"{base}{counter:02d}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def parse_structure(self, text):
        """
        Analisa a estrutura de texto para validar a hierarquia de diretórios e arquivos.
        Lança uma exceção ValueError com uma mensagem específica se a estrutura for inválida.
        """
        lines = text.splitlines()
        stack = []
        previous_level = 0

        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue  # Ignora linhas vazias

            # Calcula o nível de indentação baseado em espaços ou tabulações
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1)
            # Considera 4 espaços ou 1 tabulação por nível
            spaces = indent.count('    ')
            tabs = indent.count('\t')
            level = spaces + tabs

            # Remove os caracteres especiais como ├── ou └──
            name = re.sub(r'^[├└]──\s*', '', line.strip())

            if not name:
                raise ValueError(f"Linha {idx}: Nome do arquivo ou diretório está vazio.")

            # Verifica se é um diretório (termina com '/')
            is_dir = False
            if name.endswith('/'):
                is_dir = True
                name = name.rstrip('/')

            # Valida o nível de indentação (não pode pular níveis)
            if level > previous_level + 1:
                raise ValueError(f"Linha {idx}: Indentação inválida. Não pode pular níveis.")

            previous_level = level

            # Gerenciamento da pilha para manter a hierarquia
            if level > len(stack):
                if level == len(stack) + 1:
                    stack.append(name)
                else:
                    raise ValueError(f"Linha {idx}: Indentação inválida.")
            elif level == len(stack):
                if stack:
                    stack.pop()
                stack.append(name)
            else:
                # level < len(stack)
                for _ in range(len(stack) - level):
                    if stack:
                        stack.pop()
                    else:
                        raise ValueError(f"Linha {idx}: Estrutura de diretórios inconsistente.")
                if stack:
                    stack.pop()
                stack.append(name)

        # Se nenhuma exceção foi levantada, a estrutura é considerada válida

def main():
    """
    Função principal que inicializa e executa a aplicação PyQt5.
    """
    app = QApplication(sys.argv)
    window = FileStructureCreator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
