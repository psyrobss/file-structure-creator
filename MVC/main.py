import sys
from PyQt6.QtWidgets import QApplication
from model import FileStructureModel
from view import FileStructureView
from controller import FileStructureController

def main():
    """
    Função principal que inicializa e executa a aplicação.
    """
    app = QApplication(sys.argv)

    # Inicializar o modelo e a view
    model = FileStructureModel()
    view = FileStructureView()

    # Inicializar o controlador com o modelo e a view
    controller = FileStructureController(model, view)

    # Mostrar a interface gráfica
    view.show()

    # Executar a aplicação
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
