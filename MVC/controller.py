from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os
import logging
from model import FileStructureModel
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

    def select_directory(self):
        """
        Seleciona o diretório onde os arquivos serão criados.
        """
        directory = QFileDialog.getExistingDirectory(self.view, "Selecionar Diretório de Destino", os.getcwd())
        if directory:
            self.view.selected_directory = directory
            self.view.dir_label.setText(f"Diretório Selecionado: {directory}")
            logging.info(f"Diretório selecionado: {directory}")

    def validate_structure(self):
        """
        Valida a estrutura de arquivos e pastas inserida no editor de texto.
        """
        structure_text = self.view.text_edit.toPlainText()
        if not structure_text.strip():
            self.view.clear_tree()
            self.view.create_button.setEnabled(False)
            return

        # Constrói a estrutura
        try:
            self.model.build_structure(structure_text.splitlines())
            self.view.create_button.setEnabled(True)
            self.view.clear_tree()
            if self.model.root_nodes:
                for root_node in self.model.root_nodes:
                    self.view.add_item_to_tree(root_node)
                self.view.tree_widget.expandAll()  # Expande todos os itens para melhor visualização
        except Exception as e:
            self.view.status_bar.showMessage(f"Erro: {str(e)}")
            self.view.create_button.setEnabled(False)
            logging.error(f"Erro ao processar a estrutura: {e}")

    def create_structure(self):
        """
        Cria a estrutura de arquivos no sistema de arquivos.
        """
        if not self.view.selected_directory:
            QMessageBox.warning(self.view, "Nenhum Diretório Selecionado", "Selecione um diretório de destino.")
            return

        try:
            self.model.create_filesystem(self.view.selected_directory)
            QMessageBox.information(self.view, "Sucesso", "Estrutura de arquivos criada com sucesso!")
            logging.info("Estrutura de arquivos criada com sucesso!")
        except Exception as e:
            QMessageBox.critical(self.view, "Erro", f"Erro ao criar a estrutura: {str(e)}")
            logging.error(f"Erro ao criar a estrutura: {e}")
