# Programa organizador de archivos por extensión
# Autor: Gonzalo Cusmai

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTreeView
from PyQt6.QtGui import QFileSystemModel
import sys
import os
import shutil

class OrganizadorArchivos(QMainWindow):

    extensiones = {
        "Documentos PDF": [".pdf"],
        "Documentos Word": [".doc", ".docx"],
        "Hojas de Cálculo": [".xls", ".xlsx"],
        "Presentaciones": [".ppt", ".pptx"],
        "Imágenes": [".jpg", ".jpeg", ".png", ".gif"],
        "Videos": [".mp4", ".avi", ".mkv"],
        "Audio": [".mp3", ".wav", ".aac"],
        "Archivos Comprimidos": [".zip", ".rar", ".7z"],
        "Código Fuente": [".py", ".java", ".cpp", ".js"],
        "Ejecutables": [".exe", ".msi"],
        "Otros": []
    }
    carpeta = ""
    


    def __init__(self):
        super().__init__()
        uic.loadUi("GUIOdA.ui", self)
        self.modelo_archivos = QFileSystemModel()
        self.modelo_archivos.setRootPath("")
        self.treeView.setModel(self.modelo_archivos)

        self.botonOrdenar.clicked.connect(self.organizar_archivos)
        self.botonRuta.clicked.connect(self.seleccionar_carpeta)

    def organizar_archivos(self):
        pass

    def seleccionar_carpeta(self): # Método para seleccionar la carpeta a organizar
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if carpeta:
            self.carpeta = carpeta
            self.labelCarpeta.setText(f"Carpeta Seleccionada: {carpeta}")
            self.treeView.setRootIndex(self.modelo_archivos.index(carpeta))
            
        else:
            QMessageBox.warning(self, "Error", "No se seleccionó ninguna carpeta.")

app = QApplication(sys.argv)
ventana = OrganizadorArchivos()
ventana.show()
app.exec()