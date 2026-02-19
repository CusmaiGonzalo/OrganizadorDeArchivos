# Programa organizador de archivos por extensión
# Autor: Gonzalo Cusmai

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QTreeView, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QFileSystemModel, QIcon
from PyQt6.QtCore import Qt
import sys
import os
import shutil

import database
from GestionCategoriasDialog import GestionCategoriasDialog


def resource_path(relpath: str) -> str:
    """Devuelve la ruta absoluta a un recurso, compatible con PyInstaller."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relpath)


ICONO = resource_path(os.path.join("icono", "1485476041-artboard-1_78536.ico"))


class OrganizadorArchivos(QMainWindow):

    carpeta = ""

    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("GUIOdA.ui"), self)
        self.setWindowIcon(QIcon(ICONO))

        # Inicializar la base de datos (crea tablas y datos iniciales si no existen)
        database.inicializar_db()

        # Árbol de archivos
        self.modelo_archivos = QFileSystemModel()
        self.modelo_archivos.setRootPath("")
        self.treeView.setModel(self.modelo_archivos)

        # Reemplazar los labels estáticos del panel lateral por una lista dinámica
        self._configurar_lista_categorias()

        # Conexiones
        self.botonOrdenar.clicked.connect(self.organizar_archivos)
        self.botonRuta.clicked.connect(self.seleccionar_carpeta)
        self.actionLicencia.triggered.connect(self.Licencia)
        self.actionAcerca_de.triggered.connect(self.AcercaDe)
        self.actionComo_usar.triggered.connect(self.ComoUsar)
        self.actionCerrar_Aplicaci_n.triggered.connect(self.CerrarAplicacion)

        # Menú Herramientas → gestión de categorías (única acción)
        self.actionAgregar_Carpetas.triggered.connect(self.abrir_gestion_categorias)

    # ------------------------------------------------------------------
    def _configurar_lista_categorias(self):
        """Oculta los labels estáticos y añade un QListWidget dinámico."""
        labels_estaticos = ["label_2"]
        for nombre in labels_estaticos:
            widget = getattr(self, nombre, None)
            if widget:
                widget.hide()

        # Insertar QListWidget antes del botonOrdenar
        self.listaCategorias = QListWidget()
        self.listaCategorias.setToolTip(
            "Categorías activas. Puedes gestionarlas desde Herramientas → Gestionar Categorías."
        )
        idx = self.verticalLayout.indexOf(self.botonOrdenar)
        self.verticalLayout.insertWidget(idx, self.listaCategorias)

        self._actualizar_lista_categorias()

    def _actualizar_lista_categorias(self):
        """Recarga la lista lateral con las categorías de la DB."""
        self.listaCategorias.clear()
        for cat_id, nombre, habilitada, extensiones in database.obtener_categorias():
            item = QListWidgetItem(f"{'✔' if habilitada else '✖'} {nombre}")
            item.setToolTip("Extensiones: " + (", ".join(extensiones) if extensiones else "(ninguna)"))
            if not habilitada:
                item.setForeground(self.listaCategorias.palette().color(
                    self.listaCategorias.foregroundRole()
                ).darker(150))
            self.listaCategorias.addItem(item)

    # ------------------------------------------------------------------
    def abrir_gestion_categorias(self):
        dlg = GestionCategoriasDialog(self)
        dlg.exec()
        self._actualizar_lista_categorias()

    # ------------------------------------------------------------------
    def organizar_archivos(self):  # Método para organizar los archivos en la carpeta seleccionada
        if not self.carpeta:
            QMessageBox.warning(self, "Sin carpeta", "Primero selecciona una carpeta a organizar.")
            return

        extensiones = database.obtener_categorias_habilitadas()
        if not extensiones:
            QMessageBox.warning(self, "Sin categorías", "No hay categorías habilitadas. Activa al menos una desde Herramientas.")
            return

        try:
            # Crear carpetas para cada categoría habilitada
            for carpeta in extensiones.keys():
                ruta_carpeta = os.path.join(self.carpeta, carpeta)
                if not os.path.exists(ruta_carpeta):
                    os.makedirs(ruta_carpeta)

            # Mover archivos
            for archivo in os.listdir(self.carpeta):
                ruta_archivo = os.path.join(self.carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    extension = os.path.splitext(archivo)[1].lower()
                    movido = False
                    for categoria, ext_list in extensiones.items():
                        if extension in ext_list:
                            shutil.move(ruta_archivo, os.path.join(self.carpeta, categoria, archivo))
                            movido = True
                            break
                    if not movido:
                        # Si existe categoría "Otros" habilitada, mover ahí; si no, dejar el archivo
                        if "Otros" in extensiones:
                            shutil.move(ruta_archivo, os.path.join(self.carpeta, "Otros", archivo))

            QMessageBox.information(self, "Éxito", "¡Archivos organizados correctamente!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al organizar los archivos:\n{str(e)}")

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

    def CerrarAplicacion(self): # Método para cerrar la aplicación
        self.close()
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(ICONO))
ventana = OrganizadorArchivos()
ventana.setWindowTitle("Organizador de Archivos por Extensión")
ventana.show()
app.exec()