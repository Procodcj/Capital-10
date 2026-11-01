import customtkinter as ctk
from base_datos.conexion import obtener_conexion


class NotasFrame(ctk.CTkFrame):
    """Vista para consultar, filtrar y administrar las notas de lectura."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._crear_encabezado()
        self._crear_contenido()

    def _crear_encabezado(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="📝 Notas de Lectura",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Consulta tus conceptos clave registrados por cada libro",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(5, 0))

        btn_refrescar = ctk.CTkButton(
            header_frame,
            text="🔄 Actualizar",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=110,
            height=34,
            command=self.refrescar_datos
        )
        btn_refrescar.pack(side="right")

    def _crear_contenido(self):
        content_frame = ctk.CTkFrame(
            self,
            fg_color="#0F172A",
            corner_radius=12,
            border_width=1,
            border_color="#1E293B"
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Barra de filtro para Notas
        filtro_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        filtro_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 8))

        ctk.CTkLabel(
            filtro_frame,
            text="Filtrar por libro:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#CBD5E1"
        ).pack(side="left", padx=(0, 10))

        self.combo_filtro_libro = ctk.CTkOptionMenu(
            filtro_frame,
            values=["Todos los libros"],
            fg_color="#1E293B",
            button_color="#3B82F6",
            dropdown_hover_color="#2563EB",
            width=260,
            command=lambda _: self._cargar_notas()
        )
        self.combo_filtro_libro.set("Todos los libros")
        self.combo_filtro_libro.pack(side="left")

        self.scroll_notas = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
        self.scroll_notas.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.scroll_notas.grid_columnconfigure(0, weight=1)

        self.refrescar_datos()

    def refrescar_datos(self):
        self._actualizar_selector_libros()
        self._cargar_notas()

    def _actualizar_selector_libros(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT titulo FROM libros ORDER BY orden_reto ASC;")
        titulos = [r[0] for r in cursor.fetchall()]
        conn.close()

        opciones = ["Todos los libros"] + titulos
        seleccion_actual = self.combo_filtro_libro.get()
        self.combo_filtro_libro.configure(values=opciones)
        if seleccion_actual not in opciones:
            self.combo_filtro_libro.set("Todos los libros")

    def _cargar_notas(self):
        for widget in self.scroll_notas.winfo_children():
            widget.destroy()

        filtro = self.combo_filtro_libro.get()

        conn = obtener_conexion()
        cursor = conn.cursor()
        if filtro and filtro != "Todos los libros":
            cursor.execute("""
                SELECT n.id, l.titulo, n.capitulo, n.concepto_clave, n.fecha_creacion
                FROM notas n
                JOIN libros l ON n.libro_id = l.id
                WHERE l.titulo = ?
                ORDER BY n.id DESC;
            """, (filtro,))
        else:
            cursor.execute("""
                SELECT n.id, l.titulo, n.capitulo, n.concepto_clave, n.fecha_creacion
                FROM notas n
                JOIN libros l ON n.libro_id = l.id
                ORDER BY n.id DESC;
            """)
        notas = cursor.fetchall()
        conn.close()

        if not notas:
            ctk.CTkLabel(
                self.scroll_notas,
                text="Aún no hay notas registradas para esta selección.",
                font=ctk.CTkFont(size=13),
                text_color="#64748B"
            ).pack(pady=35)
            return

        for nota in notas:
            nota_id, titulo_libro, cap, concepto, fecha = nota

            card = ctk.CTkFrame(self.scroll_notas, fg_color="#1E293B", corner_radius=10, border_width=1, border_color="#334155")
            card.pack(fill="x", padx=8, pady=6)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(12, 4))

            cap_txt = f"  •  {cap}" if cap else ""
            ctk.CTkLabel(
                top,
                text=f"📚 {titulo_libro}{cap_txt}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#38BDF8"
            ).pack(side="left")

            btn_del = ctk.CTkButton(
                top,
                text="🗑️",
                width=30,
                height=24,
                fg_color="transparent",
                hover_color="#334155",
                text_color="#EF4444",
                command=lambda nid=nota_id: self._eliminar_nota(nid)
            )
            btn_del.pack(side="right")

            if fecha:
                ctk.CTkLabel(
                    top,
                    text=str(fecha)[:16],
                    font=ctk.CTkFont(size=11),
                    text_color="#64748B"
                ).pack(side="right", padx=10)

            ctk.CTkLabel(
                card,
                text=concepto,
                font=ctk.CTkFont(size=13),
                text_color="#F8FAFC",
                wraplength=700,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(2, 12))

    def _eliminar_nota(self, nota_id):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notas WHERE id = ?;", (nota_id,))
        conn.commit()
        conn.close()
        self._cargar_notas()
