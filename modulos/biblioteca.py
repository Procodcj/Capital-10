import customtkinter as ctk
import datetime
from collections import OrderedDict
from base_datos.conexion import obtener_conexion
from modulos.dashboard import parsear_fecha_iso, formatear_dd_mm_aaaa


def obtener_libros_completados_por_anio(conn_externa=None):
    """
    Consulta todos los libros con estado 'Completado' que tengan 'fecha_termino' registrada,
    ordenados de forma descendente por fecha, y los agrupa dinámicamente por año (YYYY)
    en orden cronológico descendente.
    """
    cerrar_al_final = False
    if conn_externa is None:
        conn = obtener_conexion()
        cerrar_al_final = True
    else:
        conn = conn_externa

    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            titulo,
            autor,
            categoria,
            total_paginas,
            paginas_leidas,
            fecha_inicio,
            COALESCE(NULLIF(TRIM(fecha_termino), ''), NULLIF(TRIM(fecha_completado), '')) AS fecha_fin_efectiva
        FROM libros
        WHERE estado = 'Completado'
          AND COALESCE(NULLIF(TRIM(fecha_termino), ''), NULLIF(TRIM(fecha_completado), '')) IS NOT NULL
        ORDER BY fecha_fin_efectiva DESC, id DESC;
    """)
    filas = cursor.fetchall()

    if cerrar_al_final:
        conn.close()

    agrupado = OrderedDict()

    for fila in filas:
        libro_id, titulo, autor, categoria, total_paginas, paginas_leidas, fecha_ini_raw, fecha_ter_raw = fila
        f_ter_obj = parsear_fecha_iso(fecha_ter_raw)
        if not f_ter_obj:
            continue

        f_ini_obj = parsear_fecha_iso(fecha_ini_raw) or f_ter_obj
        if f_ini_obj > f_ter_obj:
            f_ini_obj = f_ter_obj

        dias = max(1, (f_ter_obj - f_ini_obj).days)
        txt_dias = f"{dias} día{'s' if dias != 1 else ''}"
        rango_fechas = f"{formatear_dd_mm_aaaa(f_ini_obj)} - {formatear_dd_mm_aaaa(f_ter_obj)}"

        anio_str = f"{f_ter_obj.year:04d}"

        if anio_str not in agrupado:
            agrupado[anio_str] = []

        agrupado[anio_str].append({
            "id": libro_id,
            "titulo": titulo,
            "autor": autor,
            "categoria": categoria or "General",
            "total_paginas": total_paginas or 0,
            "paginas_leidas": paginas_leidas or total_paginas or 0,
            "fecha_inicio": f_ini_obj.isoformat(),
            "fecha_termino": f_ter_obj.isoformat(),
            "dias": dias,
            "txt_dias": txt_dias,
            "rango_fechas": rango_fechas
        })

    # Garantizar orden cronológico descendente de los años (ej. 2027, 2026, 2025)
    anios_ordenados = OrderedDict(
        sorted(agrupado.items(), key=lambda item: int(item[0]), reverse=True)
    )
    return anios_ordenados


class BibliotecaFrame(ctk.CTkFrame):
    """Vista de Biblioteca histórica de libros completados agrupados dinámicamente por año."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._crear_encabezado()

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#0F172A",
            corner_radius=12,
            border_width=1,
            border_color="#1E293B"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 20))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.refrescar_datos()

    def _crear_encabezado(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="📚 Biblioteca de Lecturas",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Historial de libros completados agrupados cronológicamente por año",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(5, 0))

    def refrescar_datos(self):
        """Recarga el historial de libros completados desde SQLite y construye las secciones por año."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        libros_por_anio = obtener_libros_completados_por_anio()

        if not libros_por_anio:
            empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1E293B", corner_radius=12)
            empty_frame.pack(fill="both", expand=True, padx=20, pady=40)

            ctk.CTkLabel(
                empty_frame,
                text="📖 Aún no hay lecturas finalizadas en tu historial",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#F8FAFC"
            ).pack(pady=(40, 8))

            ctk.CTkLabel(
                empty_frame,
                text="Cuando completes el 100% de las páginas de un libro en el Dashboard,\naparecerá automáticamente aquí agrupado en el año en que lo terminaste.",
                font=ctk.CTkFont(size=13),
                text_color="#94A3B8",
                justify="center"
            ).pack(pady=(0, 40))
            return

        for anio, lista_libros in libros_por_anio.items():
            total_anio = len(lista_libros)
            paginas_anio = sum(item["total_paginas"] for item in lista_libros)
            palabra_libro = "libro" if total_anio == 1 else "libros"

            # Contenedor independiente por año (CTkFrame tipo tarjeta/sección)
            seccion_anio = ctk.CTkFrame(
                self.scroll_frame,
                fg_color="#1E293B",
                corner_radius=12,
                border_width=1,
                border_color="#334155"
            )
            seccion_anio.pack(fill="x", padx=12, pady=(10, 14))

            # Cabecera del contenedor anual
            header_anio = ctk.CTkFrame(seccion_anio, fg_color="#0F172A", corner_radius=8)
            header_anio.pack(fill="x", padx=12, pady=(12, 10))

            ctk.CTkLabel(
                header_anio,
                text=f"🏆  Año {anio} • {total_anio} {palabra_libro}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#F8FAFC"
            ).pack(side="left", padx=14, pady=10)

            ctk.CTkLabel(
                header_anio,
                text=f"{paginas_anio} pág. leídas en {anio}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#10B981"
            ).pack(side="right", padx=14, pady=10)

            # Contenido: Fichas/filas individuales de cada libro completado en ese año
            for idx, item in enumerate(lista_libros):
                ficha = ctk.CTkFrame(
                    seccion_anio,
                    fg_color="#111827" if idx % 2 == 0 else "#172033",
                    corner_radius=8,
                    border_width=1,
                    border_color="#1E293B"
                )
                ficha.pack(fill="x", padx=12, pady=(0, 8 if idx < total_anio - 1 else 12))

                # Columna izquierda: Título y Autor
                info_izq = ctk.CTkFrame(ficha, fg_color="transparent")
                info_izq.pack(side="left", fill="x", expand=True, padx=14, pady=10)

                ctk.CTkLabel(
                    info_izq,
                    text=f"📘  {item['titulo']}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#F8FAFC",
                    anchor="w"
                ).pack(anchor="w")

                ctk.CTkLabel(
                    info_izq,
                    text=f"Autor: {item['autor']}",
                    font=ctk.CTkFont(size=12),
                    text_color="#94A3B8",
                    anchor="w"
                ).pack(anchor="w", pady=(2, 0))

                # Columna derecha: Duración (X días y rango DD/MM/AAAA - DD/MM/AAAA)
                info_der = ctk.CTkFrame(ficha, fg_color="transparent")
                info_der.pack(side="right", padx=14, pady=10)

                ctk.CTkLabel(
                    info_der,
                    text=f"⏱️ {item['txt_dias']}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#10B981",
                    anchor="e"
                ).pack(anchor="e")

                ctk.CTkLabel(
                    info_der,
                    text=item["rango_fechas"],
                    font=ctk.CTkFont(size=11),
                    text_color="#94A3B8",
                    anchor="e"
                ).pack(anchor="e", pady=(2, 0))

                # Columna central: Categoría y Páginas
                info_centro = ctk.CTkFrame(ficha, fg_color="transparent")
                info_centro.pack(side="right", padx=18, pady=10)

                ctk.CTkLabel(
                    info_centro,
                    text=item["categoria"],
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#38BDF8"
                ).pack(anchor="e")

                ctk.CTkLabel(
                    info_centro,
                    text=f"{item['total_paginas']} páginas",
                    font=ctk.CTkFont(size=11),
                    text_color="#CBD5E1"
                ).pack(anchor="e", pady=(2, 0))
