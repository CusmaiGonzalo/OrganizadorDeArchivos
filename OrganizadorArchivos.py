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
        self.actionLicencia.triggered.connect(self.Licencia)
        self.actionAcerca_de.triggered.connect(self.AcercaDe)
        self.actionComo_usar.triggered.connect(self.ComoUsar)

    def organizar_archivos(self): # Método para organizar los archivos en la carpeta seleccionada
        try:
            for carpeta in  set(self.extensiones.keys()):
                ruta_carpeta = os.path.join(self.carpeta, carpeta)
                if not os.path.exists(ruta_carpeta):
                    os.makedirs(ruta_carpeta)
        
            for archivo in os.listdir(self.carpeta):
                ruta_archivo = os.path.join(self.carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    extension = os.path.splitext(archivo)[1].lower()
                    movido = False
                    for categoria, ext_list in self.extensiones.items():
                        if extension in ext_list:
                            shutil.move(ruta_archivo, os.path.join(self.carpeta, categoria, archivo))
                            movido = True
                            break
                    if not movido:
                        shutil.move(ruta_archivo, os.path.join(self.carpeta, "Otros", archivo))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al organizar los archivos: {str(e)}")
        finally:
            QMessageBox.information(self, "Éxito", "Archivos organizados correctamente.")

    def seleccionar_carpeta(self): # Método para seleccionar la carpeta a organizar
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if carpeta:
            self.carpeta = carpeta
            self.labelCarpeta.setText(f"Carpeta Seleccionada: {carpeta}")
            self.treeView.setRootIndex(self.modelo_archivos.index(carpeta))
            
        else:
            QMessageBox.warning(self, "Error", "No se seleccionó ninguna carpeta.")

    def Licencia(self): # Método para mostrar la licencia del programa
        QMessageBox.information(self, "Licencia", "Este programa es libre de uso.\nDesarrollado por Gonzalo Cusmai.\nSoftware sin fines de lucro.")

    def AcercaDe(self): # Método para mostrar información sobre el programa
        QMessageBox.information(self, "Acerca de", "Organizador de Archivos por Extensión\nDesarrollado por Gonzalo Cusmai\nVersión 1.0")

    def ComoUsar(self): # Método para mostrar instrucciones de uso del programa
        QMessageBox.information(self, "Cómo usar", "1. Haz clic en 'Seleccionar Carpeta' para elegir la carpeta que deseas organizar.\n2. Haz clic en 'Ordenar Archivos' para organizar los archivos por extensión.\n3. Los archivos se moverán a subcarpetas según su tipo.")
app = QApplication(sys.argv)
ventana = OrganizadorArchivos()
ventana.setWindowTitle("Organizador de Archivos por Extensión")
ventana.show()
app.exec()