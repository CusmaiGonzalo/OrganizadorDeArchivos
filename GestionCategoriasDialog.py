# Diálogo para gestionar las categorías de archivos (Agregar / Modificar / Eliminar)
# Autor: Gonzalo Cusmai

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QAbstractItemView,
    QDialogButtonBox, QCheckBox, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import sys
import os
import database


def _icono() -> QIcon:
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return QIcon(os.path.join(base, "icono", "1485476041-artboard-1_78536.ico"))


# ---------------------------------------------------------------------------
# Diálogo secundario: Agregar / Editar una categoría
# ---------------------------------------------------------------------------
class EditarCategoriaDialog(QDialog):
    def __init__(self, parent=None, nombre: str = "", extensiones: list[str] = None, habilitada: bool = True):
        super().__init__(parent)
        self.setWindowTitle("Categoría")
        self.setWindowIcon(_icono())
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # --- Nombre ---
        layout.addWidget(QLabel("Nombre de la carpeta:"))
        self.inputNombre = QLineEdit(nombre)
        self.inputNombre.setPlaceholderText("Ej: Documentos PDF")
        layout.addWidget(self.inputNombre)

        # --- Extensiones ---
        layout.addWidget(QLabel("Extensiones (separadas por comas):"))
        self.inputExtensiones = QLineEdit(", ".join(extensiones) if extensiones else "")
        self.inputExtensiones.setPlaceholderText("Ej: .pdf, .doc, .txt")
        layout.addWidget(self.inputExtensiones)

        # --- Habilitada ---
        self.checkHabilitada = QCheckBox("Habilitada (usar al organizar)")
        self.checkHabilitada.setChecked(habilitada)
        layout.addWidget(self.checkHabilitada)

        # --- Botones ---
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self._aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _aceptar(self):
        nombre = self.inputNombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo requerido", "El nombre de la carpeta no puede estar vacío.")
            return
        self.accept()

    def get_datos(self) -> tuple[str, list[str], bool]:
        nombre = self.inputNombre.text().strip()
        raw = self.inputExtensiones.text()
        extensiones = [e.strip().lower() for e in raw.split(",") if e.strip()]
        # Asegurar que empiecen con punto
        extensiones = [e if e.startswith(".") else "." + e for e in extensiones]
        habilitada = self.checkHabilitada.isChecked()
        return nombre, extensiones, habilitada


# ---------------------------------------------------------------------------
# Diálogo principal: tabla con todas las categorías
# ---------------------------------------------------------------------------
class GestionCategoriasDialog(QDialog):
    COL_CHECK = 0
    COL_NOMBRE = 1
    COL_EXTENSIONES = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestionar Categorías")
        self.setWindowIcon(_icono())
        self.setMinimumSize(650, 450)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # --- Instrucción ---
        lbl = QLabel("Usa los checkboxes para habilitar o deshabilitar cada categoría.\n"
                     "Las categorías deshabilitadas no se crearán ni usarán al organizar.")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        # --- Tabla ---
        self.tabla = QTableWidget(0, 3)
        self.tabla.setHorizontalHeaderLabels(["Usar", "Carpeta", "Extensiones"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnWidth(1, 180)
        layout.addWidget(self.tabla)

        # --- Botones CRUD ---
        botonesLayout = QHBoxLayout()
        self.btnAgregar = QPushButton("Agregar")
        self.btnEditar = QPushButton("Editar")
        self.btnEliminar = QPushButton("Eliminar")
        self.btnCerrar = QPushButton("Cerrar")

        self.btnAgregar.clicked.connect(self._agregar)
        self.btnEditar.clicked.connect(self._editar)
        self.btnEliminar.clicked.connect(self._eliminar)
        self.btnCerrar.clicked.connect(self.accept)

        botonesLayout.addWidget(self.btnAgregar)
        botonesLayout.addWidget(self.btnEditar)
        botonesLayout.addWidget(self.btnEliminar)
        botonesLayout.addStretch()
        botonesLayout.addWidget(self.btnCerrar)
        layout.addLayout(botonesLayout)

        self._cargar_datos()

    # ------------------------------------------------------------------
    def _cargar_datos(self):
        """Carga (o recarga) la tabla desde la base de datos."""
        self.tabla.setRowCount(0)
        self._id_por_fila: list[int] = []  # mapeo fila → id DB

        for cat_id, nombre, habilitada, extensiones in database.obtener_categorias():
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self._id_por_fila.append(cat_id)

            # Checkbox centrado
            chk = QCheckBox()
            chk.setChecked(habilitada)
            chk.setProperty("cat_id", cat_id)
            chk.stateChanged.connect(self._checkbox_cambiado)
            widget_contenedor = self._widget_centrado(chk)
            self.tabla.setCellWidget(fila, self.COL_CHECK, widget_contenedor)

            # Nombre
            item_nombre = QTableWidgetItem(nombre)
            self.tabla.setItem(fila, self.COL_NOMBRE, item_nombre)

            # Extensiones
            item_exts = QTableWidgetItem(", ".join(extensiones) if extensiones else "(ninguna)")
            self.tabla.setItem(fila, self.COL_EXTENSIONES, item_exts)

    @staticmethod
    def _widget_centrado(widget) -> "QDialog":
        from PyQt6.QtWidgets import QWidget
        contenedor = QWidget()
        h = QHBoxLayout(contenedor)
        h.addWidget(widget)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.setContentsMargins(0, 0, 0, 0)
        return contenedor

    # ------------------------------------------------------------------
    def _checkbox_cambiado(self, estado: int):
        chk: QCheckBox = self.sender()
        cat_id = chk.property("cat_id")
        database.actualizar_habilitada(cat_id, bool(estado))

    def _fila_seleccionada(self) -> int | None:
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            QMessageBox.information(self, "Selección", "Selecciona una categoría de la tabla.")
            return None
        return filas[0].row()

    # ------------------------------------------------------------------
    def _agregar(self):
        dlg = EditarCategoriaDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nombre, extensiones, habilitada = dlg.get_datos()
            ok, error = database.agregar_categoria(nombre, extensiones, habilitada)
            if ok:
                self._cargar_datos()
            else:
                QMessageBox.critical(self, "Error", error)

    def _editar(self):
        fila = self._fila_seleccionada()
        if fila is None:
            return
        cat_id = self._id_por_fila[fila]

        # Recuperar datos actuales
        categorias = {c[0]: c for c in database.obtener_categorias()}
        _, nombre, habilitada, extensiones = categorias[cat_id]

        dlg = EditarCategoriaDialog(self, nombre=nombre, extensiones=extensiones, habilitada=habilitada)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nuevo_nombre, nuevas_exts, nueva_hab = dlg.get_datos()
            ok, error = database.modificar_categoria(cat_id, nuevo_nombre, nuevas_exts, nueva_hab)
            if ok:
                self._cargar_datos()
            else:
                QMessageBox.critical(self, "Error", error)

    def _eliminar(self):
        fila = self._fila_seleccionada()
        if fila is None:
            return
        cat_id = self._id_por_fila[fila]
        nombre = self.tabla.item(fila, self.COL_NOMBRE).text()

        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Seguro que deseas eliminar la categoría «{nombre}»?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            database.eliminar_categoria(cat_id)
            self._cargar_datos()
