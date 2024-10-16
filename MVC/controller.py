from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os
import re
import logging
from model import (
    NodeParserWithoutIndentationAndSymbols,
    NodeParserWithIndentationAndSymbols,
    FileStructureModel
)
from view import FileStructureView

class FileStructureController:
    """
    Controller que coordena a interação entre o Model (estrutura de arquivos) e o View (interface gráfica).
    """
    def __init__(self, model: FileStructureModel, view: FileStructureView):
        self.model = model
        self.view = view

        # Conectar eventos de UI
        self.view.dir_button.clicked.connect(self.select_directory)
        self.view.text_edit.textChanged.connect(self.validate_structure)
        self.view.create_button.clicked.connect(self.create_structure)
        self.view.expand_all_button.clicked.connect(self.expand_all)
        self.view.collapse_all_button.clicked.connect(self.collapse_all)

    def select_directory(self):
        """
        Seleciona o diretório onde os arquivos serão criados.
        """
        directory = QFileDialog.getExistingDirectory(
            self.view,
            "Selecionar Diretório de Destino",
            os.getcwd(),
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.view.selected_directory = directory
            self.view.dir_label.setText(f"Diretório Selecionado: {directory}")
            logging.info(f"Diretório selecionado: {directory}")
            self.view.status_bar.showMessage(f"Diretório selecionado: {directory}")

    def validate_structure(self):
        """
        Valida a estrutura de arquivos e pastas inserida no editor de texto.
        """
        structure_text = self.view.text_edit.toPlainText()
        structure_lines = structure_text.splitlines()

        if not structure_text.strip():
            self.view.clear_tree()
            self.view.create_button.setEnabled(False)
            self.view.status_bar.showMessage("Nenhuma estrutura inserida.")
            logging.info("Nenhuma estrutura inserida pelo usuário.")
            return

        # Determinar qual parser usar com base na presença de indentação ou símbolos
        if self.contains_indentation_or_symbols(structure_lines):
            parser = NodeParserWithIndentationAndSymbols()
            logging.info("Usando parser com indentação e símbolos.")
            self.view.status_bar.showMessage("Parser com indentação e símbolos selecionado.")
        else:
            parser = NodeParserWithoutIndentationAndSymbols()
            logging.info("Usando parser sem indentação e símbolos (nível zero).")
            self.view.status_bar.showMessage("Parser sem indentação e símbolos (nível zero) selecionado.")

        # Constrói a estrutura usando o parser adequado
        try:
            parser.build_structure(structure_lines)
            self.model.root_nodes = parser.root_nodes  # Transferindo a estrutura criada para o model
            self.view.create_button.setEnabled(True)
            self.view.clear_tree()

            if self.model.root_nodes:
                for root_node in self.model.root_nodes:
                    self.view.add_item_to_tree(root_node)
                self.view.tree_widget.expandAll()  # Expande todos os itens para melhor visualização

            self.view.status_bar.showMessage("Estrutura validada com sucesso.")
            logging.info("Estrutura validada com sucesso.")
        except Exception as e:
            self.view.status_bar.showMessage(f"Erro: {str(e)}")
            self.view.create_button.setEnabled(False)
            logging.error(f"Erro ao processar a estrutura: {e}")

    def create_structure(self):
        """
        Cria a estrutura de arquivos no sistema de arquivos.
        """
        if not self.view.selected_directory:
            QMessageBox.warning(
                self.view,
                "Nenhum Diretório Selecionado",
                "Selecione um diretório de destino antes de criar a estrutura."
            )
            self.view.status_bar.showMessage("Criação cancelada: Nenhum diretório selecionado.")
            logging.warning("Criação cancelada: Nenhum diretório selecionado.")
            return

        # Verificar se o diretório selecionado é válido
        if not os.path.isdir(self.view.selected_directory):
            QMessageBox.critical(
                self.view,
                "Diretório Inválido",
                "O diretório selecionado não é válido. Por favor, selecione um diretório existente."
            )
            self.view.status_bar.showMessage("Criação cancelada: Diretório inválido.")
            logging.error("Criação cancelada: Diretório inválido.")
            return

        try:
            self.model.create_filesystem(self.view.selected_directory)
            QMessageBox.information(
                self.view,
                "Sucesso",
                "Estrutura de arquivos criada com sucesso!"
            )
            self.view.status_bar.showMessage("Estrutura de arquivos criada com sucesso.")
            logging.info("Estrutura de arquivos criada com sucesso.")
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erro",
                f"Erro ao criar a estrutura: {str(e)}"
            )
            self.view.status_bar.showMessage(f"Erro ao criar a estrutura: {str(e)}")
            logging.error(f"Erro ao criar a estrutura: {e}")

    def contains_indentation_or_symbols(self, structure_lines):
        """
        Verifica se há símbolos de árvore ou indentação nas linhas.

        Args:
            - structure_lines: Lista de strings representando a estrutura de arquivos.

        Returns:
            - True se houver símbolos ou indentação, False caso contrário.
        """
        for line in structure_lines:
            # Verifica se a linha contém símbolos de árvore ou começa com espaços (indentação)
            if re.search(r'[├└─│]', line) or line.startswith(' '):
                return True
        return False

    def expand_all(self):
        """
        Expande todos os itens na árvore de diretórios.
        """
        self.view.tree_widget.expandAll()
        self.view.status_bar.showMessage("Todos os itens foram expandidos.")
        logging.info("Todos os itens foram expandidos.")

    def collapse_all(self):
        """
        Colapsa todos os itens na árvore de diretórios.
        """
        self.view.tree_widget.collapseAll()
        self.view.status_bar.showMessage("Todos os itens foram colapsados.")
        logging.info("Todos os itens foram colapsados.")
