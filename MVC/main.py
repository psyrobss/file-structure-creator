import sys
from PyQt6.QtWidgets import QApplication
from model import FileStructureModel
from view import FileStructureView
from controller import FileStructureController

def main():
    app = QApplication(sys.argv)
    
    # Inicializa o MVC
    model = FileStructureModel()
    view = FileStructureView()
    controller = FileStructureController(model, view)

    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
