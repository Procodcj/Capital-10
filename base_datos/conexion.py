import os
import sys
import sqlite3

# Determinar ruta base (compatible con desarrollo y ejecutable congelado PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "capital10.db")


def obtener_conexion():
    """Devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def reordenar_libros(conn=None):
    """
    Reenumera orden_reto de forma consecutiva (1..N) evitando colisiones
    con la restricción UNIQUE en bases de datos heredadas.
    """
    cerrar = False
    if conn is None:
        conn = obtener_conexion()
        cerrar = True

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM libros ORDER BY orden_reto ASC, id ASC;")
    ids = [row[0] for row in cursor.fetchall()]

    # Paso 1: Asignar valores negativos temporales para evitar choques con UNIQUE
    for idx, libro_id in enumerate(ids, start=1):
        cursor.execute("UPDATE libros SET orden_reto = ? WHERE id = ?;", (-idx, libro_id))

    # Paso 2: Asignar numeración positiva consecutiva 1..N
    for idx, libro_id in enumerate(ids, start=1):
        cursor.execute("UPDATE libros SET orden_reto = ? WHERE id = ?;", (idx, libro_id))

    if cerrar:
        conn.commit()
        conn.close()


def inicializar_db():
    """
    Crea la base de datos y sus tablas si no existen (0 libros por defecto para usuarios nuevos),
    y aplica migraciones automáticas compatibles con bases de datos anteriores.
    """
    conn = obtener_conexion()
    cursor = conn.cursor()

    # 1. Tabla libros (incluyendo fecha_inicio, fecha_termino y fecha_completado)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            categoria TEXT NOT NULL,
            total_paginas INTEGER DEFAULT 300,
            paginas_leidas INTEGER DEFAULT 0,
            estado TEXT NOT NULL,
            orden_reto INTEGER NOT NULL,
            fecha_completado TEXT DEFAULT NULL,
            fecha_inicio TEXT DEFAULT NULL,
            fecha_termino TEXT DEFAULT NULL
        );
    """)

    # 2. Tabla notas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            capitulo TEXT,
            concepto_clave TEXT,
            formula_metrica TEXT,
            aplicacion_portafolio TEXT,
            fecha_creacion TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (libro_id) REFERENCES libros (id) ON DELETE CASCADE
        );
    """)

    # 3. Tabla glosario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS glosario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            termino TEXT NOT NULL,
            definicion TEXT NOT NULL,
            libro_origen_id INTEGER,
            FOREIGN KEY (libro_origen_id) REFERENCES libros (id) ON DELETE SET NULL
        );
    """)

    # 4. Tabla sesiones_lectura
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_lectura (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            paginas_leidas_sesion INTEGER NOT NULL,
            fecha TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (libro_id) REFERENCES libros (id) ON DELETE CASCADE
        );
    """)

    # --- MIGRACIÓN AUTOMÁTICA Y SANEAMIENTO (Compatibilidad 100% con capital10.db existente) ---
    cursor.execute("PRAGMA table_info(libros);")
    columnas = [col[1] for col in cursor.fetchall()]

    if "fecha_completado" not in columnas:
        cursor.execute("ALTER TABLE libros ADD COLUMN fecha_completado TEXT DEFAULT NULL;")

    if "fecha_inicio" not in columnas:
        cursor.execute("ALTER TABLE libros ADD COLUMN fecha_inicio TEXT DEFAULT NULL;")

    if "fecha_termino" not in columnas:
        cursor.execute("ALTER TABLE libros ADD COLUMN fecha_termino TEXT DEFAULT NULL;")

    # Si un libro ya estaba marcado como 'Completado' pero tenía menos páginas leídas que el total,
    # igualamos paginas_leidas = total_paginas para preservar su estado Completado
    cursor.execute("""
        UPDATE libros
        SET paginas_leidas = total_paginas
        WHERE estado = 'Completado' AND total_paginas > 0 AND paginas_leidas < total_paginas;
    """)

    # Corregir libros que tienen avance parcial (0 < paginas_leidas < total_paginas) pero quedaron en 'Por leer'
    cursor.execute("""
        UPDATE libros
        SET estado = 'Leyendo', fecha_completado = NULL, fecha_termino = NULL
        WHERE paginas_leidas > 0 AND paginas_leidas < total_paginas AND estado != 'Leyendo';
    """)

    # Corregir libros que ya alcanzaron el total de páginas pero no estaban en 'Completado'
    cursor.execute("""
        UPDATE libros
        SET estado = 'Completado', paginas_leidas = total_paginas
        WHERE total_paginas > 0 AND paginas_leidas >= total_paginas AND estado != 'Completado';
    """)

    # Corregir libros con 0 páginas leídas que no estén en 'Por leer'
    cursor.execute("""
        UPDATE libros
        SET estado = 'Por leer', paginas_leidas = 0, fecha_completado = NULL, fecha_inicio = NULL, fecha_termino = NULL
        WHERE paginas_leidas <= 0 AND estado != 'Por leer';
    """)

    # Sincronizar fechas en libros 'Leyendo': asegurar fecha_inicio si está vacía
    cursor.execute("""
        UPDATE libros
        SET fecha_inicio = date('now', 'localtime')
        WHERE estado = 'Leyendo' AND (fecha_inicio IS NULL OR fecha_inicio = '');
    """)

    # Sincronizar fechas en libros 'Completado':
    # 1. Si tenía fecha_completado pero no fecha_termino, copiarla
    cursor.execute("""
        UPDATE libros
        SET fecha_termino = fecha_completado
        WHERE estado = 'Completado'
          AND (fecha_termino IS NULL OR fecha_termino = '')
          AND fecha_completado IS NOT NULL AND fecha_completado != '';
    """)

    # 2. Si sigue sin fecha_termino, asignar fecha actual
    cursor.execute("""
        UPDATE libros
        SET fecha_termino = date('now', 'localtime')
        WHERE estado = 'Completado' AND (fecha_termino IS NULL OR fecha_termino = '');
    """)

    # 3. Mantener fecha_completado sincronizada con fecha_termino
    cursor.execute("""
        UPDATE libros
        SET fecha_completado = fecha_termino
        WHERE estado = 'Completado' AND (fecha_completado IS NULL OR fecha_completado = '');
    """)

    # 4. Si un libro 'Completado' no tenía fecha_inicio, asignarle fecha_termino para evitar errores de cálculo
    cursor.execute("""
        UPDATE libros
        SET fecha_inicio = fecha_termino
        WHERE estado = 'Completado' AND (fecha_inicio IS NULL OR fecha_inicio = '');
    """)

    # Asegurar numeración consecutiva limpia en orden_reto
    reordenar_libros(conn)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    inicializar_db()
    print("Base de datos inicializada y migrada correctamente.")
