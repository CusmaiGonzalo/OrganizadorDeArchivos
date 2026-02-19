# Módulo de gestión de base de datos SQLite para el Organizador de Archivos
# Autor: Gonzalo Cusmai

import sqlite3
import os
import sys

# Si corre como ejecutable PyInstaller, la DB se guarda junto al .exe; si no, junto al script.
if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_BASE, "organizador.db")

CATEGORIAS_INICIALES = [
    ("Documentos PDF",       [".pdf"],                          True),
    ("Documentos Word",      [".doc", ".docx"],                 True),
    ("Hojas de Cálculo",     [".xls", ".xlsx"],                 True),
    ("Presentaciones",       [".ppt", ".pptx"],                 True),
    ("Imágenes",             [".jpg", ".jpeg", ".png", ".gif"], True),
    ("Videos",               [".mp4", ".avi", ".mkv"],          True),
    ("Audio",                [".mp3", ".wav", ".aac"],          True),
    ("Archivos Comprimidos", [".zip", ".rar", ".7z"],           True),
    ("Código Fuente",        [".py", ".java", ".cpp", ".js"],   True),
    ("Ejecutables",          [".exe", ".msi"],                  True),
    ("Otros",                [],                                True),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db():
    """Crea las tablas si no existen y carga los datos iniciales."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT    UNIQUE NOT NULL,
            habilitada INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extensiones (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            extension    TEXT    NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        for nombre, exts, habilitada in CATEGORIAS_INICIALES:
            cursor.execute(
                "INSERT INTO categorias (nombre, habilitada) VALUES (?, ?)",
                (nombre, 1 if habilitada else 0)
            )
            cat_id = cursor.lastrowid
            for ext in exts:
                cursor.execute(
                    "INSERT INTO extensiones (categoria_id, extension) VALUES (?, ?)",
                    (cat_id, ext.lower())
                )

    conn.commit()
    conn.close()


def obtener_categorias() -> list[tuple]:
    """Devuelve lista de (id, nombre, habilitada: bool, extensiones: list[str])."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, habilitada FROM categorias ORDER BY nombre")
    rows = cursor.fetchall()

    result = []
    for cat_id, nombre, habilitada in rows:
        cursor.execute(
            "SELECT extension FROM extensiones WHERE categoria_id = ? ORDER BY extension",
            (cat_id,)
        )
        exts = [r[0] for r in cursor.fetchall()]
        result.append((cat_id, nombre, bool(habilitada), exts))

    conn.close()
    return result


def obtener_categorias_habilitadas() -> dict[str, list[str]]:
    """Devuelve {nombre: [extensiones]} solo para categorías habilitadas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM categorias WHERE habilitada = 1")
    rows = cursor.fetchall()

    result = {}
    for cat_id, nombre in rows:
        cursor.execute(
            "SELECT extension FROM extensiones WHERE categoria_id = ?",
            (cat_id,)
        )
        result[nombre] = [r[0] for r in cursor.fetchall()]

    conn.close()
    return result


def agregar_categoria(nombre: str, extensiones: list[str], habilitada: bool = True) -> tuple[bool, str | None]:
    """Agrega una nueva categoría. Devuelve (éxito, mensaje_error)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categorias (nombre, habilitada) VALUES (?, ?)",
            (nombre.strip(), 1 if habilitada else 0)
        )
        cat_id = cursor.lastrowid
        for ext in extensiones:
            ext = ext.strip().lower()
            if ext:
                if not ext.startswith("."):
                    ext = "." + ext
                cursor.execute(
                    "INSERT INTO extensiones (categoria_id, extension) VALUES (?, ?)",
                    (cat_id, ext)
                )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, f"Ya existe una categoría con el nombre «{nombre}»."
    finally:
        conn.close()


def modificar_categoria(cat_id: int, nuevo_nombre: str, nuevas_extensiones: list[str], habilitada: bool) -> tuple[bool, str | None]:
    """Modifica una categoría existente. Devuelve (éxito, mensaje_error)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE categorias SET nombre = ?, habilitada = ? WHERE id = ?",
            (nuevo_nombre.strip(), 1 if habilitada else 0, cat_id)
        )
        cursor.execute("DELETE FROM extensiones WHERE categoria_id = ?", (cat_id,))
        for ext in nuevas_extensiones:
            ext = ext.strip().lower()
            if ext:
                if not ext.startswith("."):
                    ext = "." + ext
                cursor.execute(
                    "INSERT INTO extensiones (categoria_id, extension) VALUES (?, ?)",
                    (cat_id, ext)
                )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, f"Ya existe una categoría con el nombre «{nuevo_nombre}»."
    finally:
        conn.close()


def eliminar_categoria(cat_id: int):
    """Elimina una categoría y sus extensiones (CASCADE)."""
    conn = get_connection()
    conn.execute("DELETE FROM categorias WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()


def actualizar_habilitada(cat_id: int, habilitada: bool):
    """Actualiza solo el campo habilitada de una categoría."""
    conn = get_connection()
    conn.execute(
        "UPDATE categorias SET habilitada = ? WHERE id = ?",
        (1 if habilitada else 0, cat_id)
    )
    conn.commit()
    conn.close()
