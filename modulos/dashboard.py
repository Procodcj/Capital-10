import datetime
import customtkinter as ctk
from base_datos.conexion import obtener_conexion, reordenar_libros

CATEGORIAS_SUGERIDAS = [
    "Finanzas",
    "Inversión",
    "Hábitos",
    "Toma de Decisiones",
    "Economía",
    "Mentalidad",
    "Emprendimiento",
    "Otro"
]


def parsear_fecha_iso(cadena):
    """Convierte una cadena 'YYYY-MM-DD' (o 'DD/MM/YYYY') en objeto datetime.date, o devuelve None."""
    if not cadena:
        return None
    texto = str(cadena).strip()
    if not texto:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(texto[:10], fmt).date()
        except ValueError:
            continue
    return None


def formatear_dd_mm_aaaa(fecha_obj):
    """Devuelve DD/MM/AAAA a partir de un objeto date."""
    if not fecha_obj:
        return ""
    return fecha_obj.strftime("%d/%m/%Y")


def formatear_dd_mm_aa(fecha_obj):
    """Devuelve DD/MM/AA a partir de un objeto date."""
    if not fecha_obj:
        return ""
    return fecha_obj.strftime("%d/%m/%y")


class ModalConfirmarEliminar(ctk.CTkToplevel):
    """Ventana modal de confirmación para eliminar un libro."""

    def __init__(self, parent, titulo_libro, on_confirm_callback):
        super().__init__(parent)
        self.on_confirm_callback = on_confirm_callback

        self.title("Confirmar Eliminación")
        self.geometry("420x220")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=12, border_width=1, border_color="#334155")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="⚠️ ¿Eliminar este libro?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC"
        ).pack(padx=15, pady=(18, 6))

        ctk.CTkLabel(
            frame,
            text=f"Se eliminará \"{titulo_libro}\" junto con sus notas y sesiones de lectura registradas.",
            font=ctk.CTkFont(size=12),
            text_color="#CBD5E1",
            wraplength=350,
            justify="center"
        ).pack(padx=15, pady=(0, 18))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=120,
            height=34,
            fg_color="#334155",
            hover_color="#475569",
            command=self.destroy
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Sí, Eliminar",
            width=130,
            height=34,
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._confirmar
        ).pack(side="left", padx=8)

    def _confirmar(self):
        self.destroy()
        if self.on_confirm_callback:
            self.on_confirm_callback()


class ModalNuevoLibro(ctk.CTkToplevel):
    """Ventana modal para agregar un nuevo libro al reto."""

    def __init__(self, parent, on_create_callback):
        super().__init__(parent)
        self.on_create_callback = on_create_callback
        self._actualizando_auto = False

        self.title("Agregar Nuevo Libro")
        self.geometry("520x580")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="➕ Agregar Nuevo Libro",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F8FAFC"
        ).pack(anchor="w", padx=20, pady=(15, 2))

        ctk.CTkLabel(
            header,
            text="Registra un nuevo título en tu lista personalizada de lectura",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        body = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=10)
        body.pack(fill="both", expand=True, padx=20, pady=15)

        # Título
        ctk.CTkLabel(body, text="Título del Libro:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", padx=20, pady=(15, 3))
        self.entry_titulo = ctk.CTkEntry(body, placeholder_text="Ej: El Inversor Inteligente", fg_color="#0F172A", border_color="#334155")
        self.entry_titulo.pack(fill="x", padx=20, pady=(0, 10))

        # Autor
        ctk.CTkLabel(body, text="Autor:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", padx=20, pady=(2, 3))
        self.entry_autor = ctk.CTkEntry(body, placeholder_text="Ej: Benjamin Graham", fg_color="#0F172A", border_color="#334155")
        self.entry_autor.pack(fill="x", padx=20, pady=(0, 10))

        # Categoría
        ctk.CTkLabel(body, text="Categoría / Tema:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").pack(anchor="w", padx=20, pady=(2, 3))
        self.combo_categoria = ctk.CTkOptionMenu(
            body,
            values=CATEGORIAS_SUGERIDAS,
            fg_color="#0F172A",
            button_color="#3B82F6",
            dropdown_hover_color="#2563EB",
            command=self._on_categoria_change
        )
        self.combo_categoria.set("Finanzas")
        self.combo_categoria.pack(fill="x", padx=20, pady=(0, 10))

        # Contenedor dinámico para Categoría personalizada ("Otro")
        self.frame_cat_otro = ctk.CTkFrame(body, fg_color="transparent")
        ctk.CTkLabel(
            self.frame_cat_otro,
            text="Especificar Categoría Personalizada:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#CBD5E1"
        ).pack(anchor="w", pady=(0, 3))
        self.entry_categoria_otro = ctk.CTkEntry(
            self.frame_cat_otro,
            placeholder_text="Escribe tu categoría personalizada...",
            fg_color="#0F172A",
            border_color="#334155"
        )
        self.entry_categoria_otro.pack(fill="x", pady=(0, 10))

        # Fila para Páginas Totales, Páginas Leídas y Estado
        self.row_nums = ctk.CTkFrame(body, fg_color="transparent")
        self.row_nums.pack(fill="x", padx=20, pady=(5, 10))
        self.row_nums.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(self.row_nums, text="Páginas Totales:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 3))
        self.entry_total = ctk.CTkEntry(self.row_nums, fg_color="#0F172A", border_color="#334155")
        self.entry_total.insert(0, "300")
        self.entry_total.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.entry_total.bind("<KeyRelease>", self._on_paginas_change)

        ctk.CTkLabel(self.row_nums, text="Páginas Leídas:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=1, sticky="w", padx=4, pady=(0, 3))
        self.entry_leidas = ctk.CTkEntry(self.row_nums, fg_color="#0F172A", border_color="#334155")
        self.entry_leidas.insert(0, "0")
        self.entry_leidas.grid(row=1, column=1, sticky="ew", padx=4)
        self.entry_leidas.bind("<KeyRelease>", self._on_paginas_change)

        ctk.CTkLabel(self.row_nums, text="Estado (Automático):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=2, sticky="w", padx=(8, 0), pady=(0, 3))
        self.combo_estado = ctk.CTkOptionMenu(
            self.row_nums,
            values=["Por leer", "Leyendo", "Completado"],
            fg_color="#0F172A",
            button_color="#3B82F6",
            dropdown_hover_color="#2563EB",
            command=self._on_estado_change
        )
        self.combo_estado.set("Por leer")
        self.combo_estado.grid(row=1, column=2, sticky="ew", padx=(8, 0))

        self.lbl_status = ctk.CTkLabel(body, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_status.pack(anchor="w", padx=20, pady=(5, 5))

        btn_guardar = ctk.CTkButton(
            body,
            text="💾 Agregar Libro",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=self._guardar_nuevo
        )
        btn_guardar.pack(fill="x", padx=20, pady=(5, 15))

    def _on_categoria_change(self, seleccion):
        """Muestra u oculta dinámicamente el campo de texto para categoría personalizada."""
        if seleccion == "Otro":
            self.frame_cat_otro.pack(fill="x", padx=20, before=self.row_nums)
            self.entry_categoria_otro.focus_set()
        else:
            self.frame_cat_otro.pack_forget()

    def _on_paginas_change(self, event=None):
        if self._actualizando_auto:
            return
        val_tot = self.entry_total.get().strip()
        val_lei = self.entry_leidas.get().strip()
        if not val_tot.isdigit() or not val_lei.isdigit():
            return
        tot = int(val_tot)
        lei = int(val_lei)
        if tot <= 0:
            return

        self._actualizando_auto = True
        if lei <= 0:
            self.combo_estado.set("Por leer")
        elif lei >= tot:
            self.combo_estado.set("Completado")
        else:
            self.combo_estado.set("Leyendo")
        self._actualizando_auto = False

    def _on_estado_change(self, estado_elegido):
        if self._actualizando_auto:
            return
        val_tot = self.entry_total.get().strip()
        tot = int(val_tot) if val_tot.isdigit() and int(val_tot) > 0 else 300

        self._actualizando_auto = True
        if estado_elegido == "Completado":
            self.entry_leidas.delete(0, "end")
            self.entry_leidas.insert(0, str(tot))
        elif estado_elegido == "Por leer":
            self.entry_leidas.delete(0, "end")
            self.entry_leidas.insert(0, "0")
        elif estado_elegido == "Leyendo":
            val_lei = self.entry_leidas.get().strip()
            lei = int(val_lei) if val_lei.isdigit() else 0
            if lei <= 0 or lei >= tot:
                self.entry_leidas.delete(0, "end")
                self.entry_leidas.insert(0, "1" if tot > 1 else "0")
        self._actualizando_auto = False

    def _guardar_nuevo(self):
        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()
        cat_sel = self.combo_categoria.get().strip()
        if cat_sel == "Otro":
            categoria = self.entry_categoria_otro.get().strip()
            if not categoria:
                self.lbl_status.configure(text="❌ Por favor escribe la categoría personalizada.", text_color="#EF4444")
                return
        else:
            categoria = cat_sel or "General"

        val_tot = self.entry_total.get().strip()
        val_lei = self.entry_leidas.get().strip()

        if not titulo or not autor:
            self.lbl_status.configure(text="❌ El título y el autor son obligatorios.", text_color="#EF4444")
            return

        if not val_tot.isdigit() or not val_lei.isdigit():
            self.lbl_status.configure(text="❌ Las páginas deben ser números enteros válidos.", text_color="#EF4444")
            return

        tot_paginas = int(val_tot)
        paginas_leidas = int(val_lei)

        if tot_paginas <= 0:
            self.lbl_status.configure(text="❌ Las páginas totales deben ser mayores a 0.", text_color="#EF4444")
            return

        if paginas_leidas < 0 or paginas_leidas > tot_paginas:
            self.lbl_status.configure(text=f"❌ Las páginas leídas deben estar entre 0 y {tot_paginas}.", text_color="#EF4444")
            return

        hoy_iso = datetime.date.today().isoformat()

        # Determinar estado y fechas automáticas según las páginas
        if paginas_leidas == 0:
            estado = "Por leer"
            fecha_ini = None
            fecha_ter = None
            fecha_comp = None
        elif paginas_leidas == tot_paginas:
            estado = "Completado"
            fecha_ini = hoy_iso
            fecha_ter = hoy_iso
            fecha_comp = hoy_iso
        else:
            estado = "Leyendo"
            fecha_ini = hoy_iso
            fecha_ter = None
            fecha_comp = None

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(MAX(orden_reto), 0) + 1 FROM libros;")
        siguiente_orden = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO libros (orden_reto, titulo, autor, categoria, total_paginas, paginas_leidas, estado, fecha_completado, fecha_inicio, fecha_termino)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (siguiente_orden, titulo, autor, categoria, tot_paginas, paginas_leidas, estado, fecha_comp, fecha_ini, fecha_ter))

        libro_id = cursor.lastrowid
        if paginas_leidas > 0:
            cursor.execute("INSERT INTO sesiones_lectura (libro_id, paginas_leidas_sesion) VALUES (?, ?);", (libro_id, paginas_leidas))

        reordenar_libros(conn)
        conn.commit()
        conn.close()

        if self.on_create_callback:
            self.on_create_callback()
        self.destroy()


class ModalGestionLibro(ctk.CTkToplevel):
    """Ventana modal para gestionar datos, avance de lectura, fechas, notas y eliminación de un libro."""

    def __init__(self, parent, libro, on_update_callback):
        super().__init__(parent)
        (
            self.libro_id,
            self.orden,
            self.titulo,
            self.autor,
            self.categoria,
            self.total_paginas,
            self.paginas_leidas,
            self.estado,
            self.fecha_completado,
            self.fecha_inicio,
            self.fecha_termino
        ) = libro
        self.on_update_callback = on_update_callback
        self._actualizando_auto = False

        self.title(f"Gestionar Libro: {self.titulo}")
        self.geometry("650x575")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._crear_interfaz()

    def _crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)

        header_top = ctk.CTkFrame(header, fg_color="transparent")
        header_top.pack(fill="x", padx=20, pady=(15, 2))

        self.lbl_titulo_header = ctk.CTkLabel(
            header_top,
            text=f"📚 {self.titulo}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F8FAFC"
        )
        self.lbl_titulo_header.pack(side="left")

        btn_eliminar = ctk.CTkButton(
            header_top,
            text="🗑️ Eliminar Libro",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=125,
            height=30,
            command=self._solicitar_eliminar
        )
        btn_eliminar.pack(side="right")

        self.lbl_subtitulo_header = ctk.CTkLabel(
            header,
            text=self._texto_subtitulo(),
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8"
        )
        self.lbl_subtitulo_header.pack(anchor="w", padx=20, pady=(0, 15))

        tabview = ctk.CTkTabview(self, fg_color="#1E293B", segmented_button_selected_color="#3B82F6", corner_radius=10)
        tabview.pack(fill="both", expand=True, padx=20, pady=15)

        tab_avance = tabview.add("📈 Datos y Avance")
        tab_nota = tabview.add("📝 Agregar Nota")

        self._configurar_tab_avance(tab_avance)
        self._configurar_tab_nota(tab_nota)

    def _texto_subtitulo(self):
        partes = [
            f"Autor: {self.autor}",
            f"Categoría: {self.categoria}",
            f"Páginas: {self.paginas_leidas}/{self.total_paginas}"
        ]
        f_ini = parsear_fecha_iso(self.fecha_inicio)
        f_ter = parsear_fecha_iso(self.fecha_termino)
        if self.estado == "Leyendo" and f_ini:
            partes.append(f"Inicio: {formatear_dd_mm_aaaa(f_ini)}")
        elif self.estado == "Completado" and f_ter:
            partes.append(f"Término: {formatear_dd_mm_aaaa(f_ter)}")
        return "  •  ".join(partes)

    def _configurar_tab_avance(self, parent):
        parent.columnconfigure((0, 1), weight=1)

        # Fila 1: Título y Autor
        ctk.CTkLabel(parent, text="Título del Libro:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=0, sticky="w", padx=15, pady=(10, 3))
        self.entry_titulo = ctk.CTkEntry(parent, fg_color="#0F172A", border_color="#334155")
        self.entry_titulo.insert(0, self.titulo)
        self.entry_titulo.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        ctk.CTkLabel(parent, text="Autor:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=0, column=1, sticky="w", padx=15, pady=(10, 3))
        self.entry_autor = ctk.CTkEntry(parent, fg_color="#0F172A", border_color="#334155")
        self.entry_autor.insert(0, self.autor)
        self.entry_autor.grid(row=1, column=1, sticky="ew", padx=15, pady=(0, 10))

        # Fila 2: Categoría y Estado Automático
        ctk.CTkLabel(parent, text="Categoría / Tema:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=2, column=0, sticky="w", padx=15, pady=(5, 3))
        valores_cat = list(CATEGORIAS_SUGERIDAS)
        if self.categoria not in valores_cat:
            valores_cat.insert(0, self.categoria)
        self.combo_categoria = ctk.CTkOptionMenu(
            parent,
            values=valores_cat,
            fg_color="#0F172A",
            button_color="#3B82F6",
            dropdown_hover_color="#2563EB",
            command=self._on_categoria_edit_change
        )
        self.combo_categoria.set(self.categoria)
        self.combo_categoria.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 10))

        ctk.CTkLabel(parent, text="Estado de Lectura (Automático):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=2, column=1, sticky="w", padx=15, pady=(5, 3))
        self.combo_estado = ctk.CTkOptionMenu(
            parent,
            values=["Por leer", "Leyendo", "Completado"],
            fg_color="#0F172A",
            button_color="#3B82F6",
            dropdown_hover_color="#2563EB",
            command=self._on_estado_change
        )
        self.combo_estado.set(self.estado)
        self.combo_estado.grid(row=3, column=1, sticky="ew", padx=15, pady=(0, 10))

        # Fila opcional para Categoría "Otro" en edición
        self.lbl_cat_otro_edit = ctk.CTkLabel(parent, text="Categoría Personalizada:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1")
        self.entry_cat_otro_edit = ctk.CTkEntry(parent, placeholder_text="Escribe la categoría...", fg_color="#0F172A", border_color="#334155")

        # Fila 3: Páginas Leídas y Páginas Totales
        ctk.CTkLabel(parent, text="Páginas Leídas:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=5, column=0, sticky="w", padx=15, pady=(5, 3))
        self.entry_paginas = ctk.CTkEntry(parent, fg_color="#0F172A", border_color="#334155")
        self.entry_paginas.insert(0, str(self.paginas_leidas))
        self.entry_paginas.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.entry_paginas.bind("<KeyRelease>", self._on_paginas_change)

        ctk.CTkLabel(parent, text="Páginas Totales:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CBD5E1").grid(row=5, column=1, sticky="w", padx=15, pady=(5, 3))
        self.entry_total_paginas = ctk.CTkEntry(parent, fg_color="#0F172A", border_color="#334155")
        self.entry_total_paginas.insert(0, str(self.total_paginas))
        self.entry_total_paginas.grid(row=6, column=1, sticky="ew", padx=15, pady=(0, 10))
        self.entry_total_paginas.bind("<KeyRelease>", self._on_paginas_change)

        # Fila 4: Fecha de Inicio (editable) y Botón Guardar alineados simétricamente
        ctk.CTkLabel(
            parent,
            text="Fecha de Inicio (DD/MM/AAAA):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#CBD5E1"
        ).grid(row=7, column=0, sticky="w", padx=15, pady=(5, 3))
        self.entry_fecha_inicio = ctk.CTkEntry(
            parent,
            placeholder_text="Ej: 25/01/2026",
            fg_color="#0F172A",
            border_color="#334155",
            height=34
        )
        f_ini_actual = parsear_fecha_iso(self.fecha_inicio)
        if f_ini_actual:
            self.entry_fecha_inicio.insert(0, formatear_dd_mm_aaaa(f_ini_actual))
        self.entry_fecha_inicio.grid(row=8, column=0, sticky="ew", padx=15, pady=(0, 10))

        btn_guardar = ctk.CTkButton(
            parent,
            text="💾 Guardar Avance y Datos",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=34,
            command=self._guardar_avance
        )
        btn_guardar.grid(row=8, column=1, sticky="ew", padx=15, pady=(0, 10))

        self.lbl_status_avance = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_status_avance.grid(row=9, column=0, columnspan=2, sticky="w", padx=15, pady=4)

    def _on_categoria_edit_change(self, seleccion):
        if seleccion == "Otro":
            self.lbl_cat_otro_edit.grid(row=4, column=0, sticky="w", padx=15, pady=(2, 2))
            self.entry_cat_otro_edit.grid(row=4, column=1, sticky="ew", padx=15, pady=(2, 8))
            self.entry_cat_otro_edit.focus_set()
        else:
            self.lbl_cat_otro_edit.grid_remove()
            self.entry_cat_otro_edit.grid_remove()

    def _on_paginas_change(self, event=None):
        """Actualiza automáticamente el selector de estado y la fecha de inicio según las páginas ingresadas."""
        if self._actualizando_auto:
            return
        val_pag = self.entry_paginas.get().strip()
        val_tot = self.entry_total_paginas.get().strip()
        if not val_pag.isdigit() or not val_tot.isdigit():
            return

        pag = int(val_pag)
        tot = int(val_tot)
        if tot <= 0:
            return

        self._actualizando_auto = True
        hoy_str = formatear_dd_mm_aaaa(datetime.date.today())
        if pag <= 0:
            nuevo_est = "Por leer"
            self.entry_fecha_inicio.delete(0, "end")
        elif pag >= tot:
            nuevo_est = "Completado"
            if not self.entry_fecha_inicio.get().strip():
                self.entry_fecha_inicio.insert(0, hoy_str)
        else:
            nuevo_est = "Leyendo"
            if not self.entry_fecha_inicio.get().strip():
                self.entry_fecha_inicio.insert(0, hoy_str)
        self.combo_estado.set(nuevo_est)
        self._actualizando_auto = False

    def _on_estado_change(self, estado_elegido):
        """Actualiza automáticamente las páginas leídas y la fecha de inicio si el usuario cambia el estado manualmente."""
        if self._actualizando_auto:
            return
        val_tot = self.entry_total_paginas.get().strip()
        tot = int(val_tot) if val_tot.isdigit() and int(val_tot) > 0 else self.total_paginas

        self._actualizando_auto = True
        hoy_str = formatear_dd_mm_aaaa(datetime.date.today())
        if estado_elegido == "Completado":
            self.entry_paginas.delete(0, "end")
            self.entry_paginas.insert(0, str(tot))
            if not self.entry_fecha_inicio.get().strip():
                self.entry_fecha_inicio.insert(0, hoy_str)
        elif estado_elegido == "Por leer":
            self.entry_paginas.delete(0, "end")
            self.entry_paginas.insert(0, "0")
            self.entry_fecha_inicio.delete(0, "end")
        elif estado_elegido == "Leyendo":
            val_pag = self.entry_paginas.get().strip()
            pag = int(val_pag) if val_pag.isdigit() else 0
            if pag <= 0 or pag >= tot:
                self.entry_paginas.delete(0, "end")
                self.entry_paginas.insert(0, "1" if tot > 1 else "0")
            if not self.entry_fecha_inicio.get().strip():
                self.entry_fecha_inicio.insert(0, hoy_str)
        self._actualizando_auto = False

    def _guardar_avance(self):
        nuevo_titulo = self.entry_titulo.get().strip()
        nuevo_autor = self.entry_autor.get().strip()
        cat_sel = self.combo_categoria.get().strip()
        if cat_sel == "Otro":
            nueva_cat = self.entry_cat_otro_edit.get().strip()
            if not nueva_cat:
                self.lbl_status_avance.configure(text="❌ Escribe la categoría personalizada.", text_color="#EF4444")
                return
        else:
            nueva_cat = cat_sel or "General"

        val_pag = self.entry_paginas.get().strip()
        val_tot_pag = self.entry_total_paginas.get().strip()

        if not nuevo_titulo or not nuevo_autor:
            self.lbl_status_avance.configure(text="❌ El título y el autor no pueden estar vacíos.", text_color="#EF4444")
            return

        if not val_pag.isdigit() or not val_tot_pag.isdigit():
            self.lbl_status_avance.configure(text="❌ Ingrese números válidos para páginas leídas y totales.", text_color="#EF4444")
            return

        paginas = int(val_pag)
        tot_paginas = int(val_tot_pag)

        if tot_paginas <= 0:
            self.lbl_status_avance.configure(text="❌ Las páginas totales deben ser mayores a 0.", text_color="#EF4444")
            return

        if paginas < 0 or paginas > tot_paginas:
            self.lbl_status_avance.configure(text=f"❌ Las páginas leídas deben estar entre 0 y {tot_paginas}.", text_color="#EF4444")
            return

        # Regla automática estricta de estado según páginas
        if paginas == 0:
            nuevo_estado = "Por leer"
        elif paginas == tot_paginas:
            nuevo_estado = "Completado"
        else:
            nuevo_estado = "Leyendo"

        self._actualizando_auto = True
        self.combo_estado.set(nuevo_estado)
        self._actualizando_auto = False

        hoy_obj = datetime.date.today()
        txt_fecha_ini = self.entry_fecha_inicio.get().strip()

        # Lógica de Fecha de Inicio (editable) y Fecha de Término (100% automática)
        if paginas == 0:
            nueva_fecha_inicio = None
            nueva_fecha_termino = None
            nueva_fecha_comp = None
            self.entry_fecha_inicio.delete(0, "end")
        else:
            if txt_fecha_ini:
                fecha_ini_obj = parsear_fecha_iso(txt_fecha_ini)
                if not fecha_ini_obj:
                    self.lbl_status_avance.configure(
                        text="❌ Fecha de Inicio inválida. Usa el formato DD/MM/AAAA.",
                        text_color="#EF4444"
                    )
                    return
            else:
                fecha_ini_obj = hoy_obj

            if nuevo_estado == "Completado":
                f_ter_previa = parsear_fecha_iso(self.fecha_termino)
                fecha_ter_obj = f_ter_previa if (self.estado == "Completado" and f_ter_previa) else hoy_obj
                if fecha_ini_obj > fecha_ter_obj:
                    self.lbl_status_avance.configure(
                        text="❌ La Fecha de Inicio no puede ser posterior a la fecha de término.",
                        text_color="#EF4444"
                    )
                    return
                nueva_fecha_inicio = fecha_ini_obj.isoformat()
                nueva_fecha_termino = fecha_ter_obj.isoformat()
                nueva_fecha_comp = nueva_fecha_termino
            else:  # "Leyendo"
                nueva_fecha_inicio = fecha_ini_obj.isoformat()
                nueva_fecha_termino = None
                nueva_fecha_comp = None

            self.entry_fecha_inicio.delete(0, "end")
            self.entry_fecha_inicio.insert(0, formatear_dd_mm_aaaa(fecha_ini_obj))

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE libros
            SET titulo = ?, autor = ?, categoria = ?, paginas_leidas = ?, total_paginas = ?,
                estado = ?, fecha_completado = ?, fecha_inicio = ?, fecha_termino = ?
            WHERE id = ?;
        """, (
            nuevo_titulo,
            nuevo_autor,
            nueva_cat,
            paginas,
            tot_paginas,
            nuevo_estado,
            nueva_fecha_comp,
            nueva_fecha_inicio,
            nueva_fecha_termino,
            self.libro_id
        ))

        diferencia = paginas - self.paginas_leidas
        if diferencia > 0:
            cursor.execute("INSERT INTO sesiones_lectura (libro_id, paginas_leidas_sesion) VALUES (?, ?);", (self.libro_id, diferencia))

        conn.commit()
        conn.close()

        self.titulo = nuevo_titulo
        self.autor = nuevo_autor
        self.categoria = nueva_cat
        self.paginas_leidas = paginas
        self.total_paginas = tot_paginas
        self.estado = nuevo_estado
        self.fecha_completado = nueva_fecha_comp
        self.fecha_inicio = nueva_fecha_inicio
        self.fecha_termino = nueva_fecha_termino

        self.title(f"Gestionar Libro: {self.titulo}")
        self.lbl_titulo_header.configure(text=f"📚 {self.titulo}")
        self.lbl_subtitulo_header.configure(text=self._texto_subtitulo())
        self.lbl_status_avance.configure(text="✅ Datos, fechas y avance guardados correctamente.", text_color="#10B981")

        if self.on_update_callback:
            self.on_update_callback()

    def _solicitar_eliminar(self):
        ModalConfirmarEliminar(self, self.titulo, on_confirm_callback=self._eliminar_libro)

    def _eliminar_libro(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM libros WHERE id = ?;", (self.libro_id,))
        reordenar_libros(conn)
        conn.commit()
        conn.close()

        if self.on_update_callback:
            self.on_update_callback()
        self.destroy()

    def _configurar_tab_nota(self, parent):
        parent.columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Capítulo:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#CBD5E1").pack(anchor="w", padx=15, pady=(15, 4))
        self.entry_capitulo = ctk.CTkEntry(parent, placeholder_text="Ej: Cap. 4 - Los 4 pasos del hábito", fg_color="#0F172A", border_color="#334155", height=36)
        self.entry_capitulo.pack(fill="x", padx=15, pady=(0, 14))

        ctk.CTkLabel(parent, text="Concepto Clave:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#CBD5E1").pack(anchor="w", padx=15, pady=(2, 4))
        self.txt_concepto = ctk.CTkTextbox(parent, height=130, fg_color="#0F172A", border_color="#334155", border_width=1)
        self.txt_concepto.pack(fill="x", padx=15, pady=(0, 15))

        btn_guardar_nota = ctk.CTkButton(
            parent,
            text="📌 Guardar Nota",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=38,
            command=self._guardar_nota
        )
        btn_guardar_nota.pack(anchor="w", padx=15, pady=5)

        self.lbl_status_nota = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_status_nota.pack(anchor="w", padx=15, pady=5)

    def _guardar_nota(self):
        capitulo = self.entry_capitulo.get().strip()
        concepto = self.txt_concepto.get("1.0", "end-1c").strip()

        if not concepto:
            self.lbl_status_nota.configure(text="❌ El concepto clave es obligatorio.", text_color="#EF4444")
            return

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notas (libro_id, capitulo, concepto_clave, formula_metrica, aplicacion_portafolio)
            VALUES (?, ?, ?, '', '');
        """, (self.libro_id, capitulo, concepto))
        conn.commit()
        conn.close()

        self.entry_capitulo.delete(0, "end")
        self.txt_concepto.delete("1.0", "end")

        self.lbl_status_nota.configure(text="✅ Nota guardada correctamente.", text_color="#10B981")


class DashboardFrame(ctk.CTkFrame):
    """Vista principal del Dashboard con gestión dinámica de libros, duración y contador anual."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._crear_encabezado()

        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        for i in range(4):
            self.kpi_frame.grid_columnconfigure(i, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#0F172A", corner_radius=12, border_width=1, border_color="#1E293B")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        self.refrescar_datos()

    def _crear_encabezado(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard de Lectura",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Haz clic en cualquier libro para editar su avance, fechas, notas o eliminarlo",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(5, 0))

        btn_nuevo = ctk.CTkButton(
            header_frame,
            text="➕ Agregar Libro",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            corner_radius=8,
            command=self._abrir_modal_nuevo
        )
        btn_nuevo.pack(side="right")

    def refrescar_datos(self):
        """Vuelve a cargar los datos de la BD y reconstruye los KPIs y la tabla de libros."""
        self._refrescar_kpi()
        self._refrescar_tabla()

    def _refrescar_kpi(self):
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM libros;")
        total = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM libros WHERE estado = 'Completado';")
        completados = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM libros WHERE estado = 'Leyendo';")
        leyendo = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(paginas_leidas), SUM(total_paginas) FROM libros;")
        row_pag = cursor.fetchone()
        pag_leidas = row_pag[0] or 0
        pag_totales = row_pag[1] or 0
        conn.close()

        porcentaje = int((pag_leidas / pag_totales) * 100) if pag_totales > 0 else 0

        tarjetas = [
            ("Total Libros", f"{total}", "#3B82F6", "📚"),
            ("Completados", f"{completados} / {total}", "#10B981", "✅"),
            ("En Lectura", f"{leyendo}", "#F59E0B", "📖"),
            ("Páginas Leídas (Global)", f"{pag_leidas} / {pag_totales} pág. ({porcentaje}%)", "#8B5CF6", "📈")
        ]

        for idx, (titulo, val, color, icono) in enumerate(tarjetas):
            card = ctk.CTkFrame(self.kpi_frame, fg_color="#1E293B", corner_radius=12, border_width=1, border_color="#334155")
            card.grid(row=0, column=idx, padx=6, pady=5, sticky="ew")

            top_lbl = ctk.CTkLabel(card, text=f"{icono}  {titulo}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8")
            top_lbl.pack(anchor="w", padx=14, pady=(12, 4))

            tam_fuente = 16 if idx == 3 else 18
            val_lbl = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=tam_fuente, weight="bold"), text_color=color)
            val_lbl.pack(anchor="w", padx=14, pady=(0, 12))

    def _refrescar_tabla(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, orden_reto, titulo, autor, categoria, total_paginas, paginas_leidas, estado, fecha_completado, fecha_inicio, fecha_termino
            FROM libros
            ORDER BY orden_reto ASC;
        """)
        libros = cursor.fetchall()
        conn.close()

        if not libros:
            empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1E293B", corner_radius=12)
            empty_frame.pack(fill="both", expand=True, padx=20, pady=40)

            ctk.CTkLabel(
                empty_frame,
                text="📚 Tu biblioteca de lectura está vacía",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#F8FAFC"
            ).pack(pady=(35, 8))

            ctk.CTkLabel(
                empty_frame,
                text="Aún no has registrado libros en tu reto. Haz clic en '+ Agregar Libro' para añadir tu primera lectura.",
                font=ctk.CTkFont(size=13),
                text_color="#94A3B8"
            ).pack(pady=(0, 20))

            ctk.CTkButton(
                empty_frame,
                text="➕ Agregar mi primer libro",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                height=38,
                command=self._abrir_modal_nuevo
            ).pack(pady=(0, 35))
            return

        headers = ["#", "Título del Libro", "Autor", "Categoría", "Progreso", "Duración", "Estado", "Acción"]
        cols_w = [28, 185, 118, 100, 152, 125, 95, 70]

        header_row = ctk.CTkFrame(self.scroll_frame, fg_color="#1E293B", corner_radius=8)
        header_row.pack(fill="x", padx=5, pady=(5, 10))

        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_row,
                text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#CBD5E1",
                width=cols_w[idx],
                anchor="w" if idx in [1, 2, 3, 4] else "center"
            )
            lbl.pack(side="left", padx=6, pady=8)

        badge_colors = {
            "Completado": ("#065F46", "#10B981"),
            "Leyendo": ("#78350F", "#F59E0B"),
            "Por leer": ("#1E293B", "#64748B")
        }

        hoy = datetime.date.today()

        for libro in libros:
            libro_id, orden, titulo, autor, cat, tot_pag, pag_lei, estado, fecha_comp, fecha_ini, fecha_ter = libro

            row = ctk.CTkFrame(self.scroll_frame, fg_color="#1E293B" if orden % 2 == 0 else "#111827", corner_radius=6)
            row.pack(fill="x", padx=5, pady=3)

            # 0. Orden
            ctk.CTkLabel(row, text=str(orden), font=ctk.CTkFont(size=12, weight="bold"), text_color="#64748B", width=cols_w[0]).pack(side="left", padx=6)
            # 1. Título
            ctk.CTkLabel(row, text=titulo, font=ctk.CTkFont(size=13, weight="bold"), text_color="#F8FAFC", width=cols_w[1], anchor="w").pack(side="left", padx=6)
            # 2. Autor
            ctk.CTkLabel(row, text=autor, font=ctk.CTkFont(size=12), text_color="#94A3B8", width=cols_w[2], anchor="w").pack(side="left", padx=6)
            # 3. Categoría
            ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(size=12), text_color="#38BDF8", width=cols_w[3], anchor="w").pack(side="left", padx=6)

            # 4. Progreso
            prog_frame = ctk.CTkFrame(row, fg_color="transparent", width=cols_w[4])
            prog_frame.pack(side="left", padx=6)

            ratio = (pag_lei / tot_pag) if tot_pag > 0 else 0
            porc_libro = int(ratio * 100)
            pbar = ctk.CTkProgressBar(prog_frame, width=62, height=8, progress_color="#10B981" if ratio == 1 else "#3B82F6")
            pbar.set(ratio)
            pbar.pack(side="left", padx=(0, 5))

            ctk.CTkLabel(prog_frame, text=f"{pag_lei}/{tot_pag} ({porc_libro}%)", font=ctk.CTkFont(size=10), text_color="#94A3B8").pack(side="left")

            # 5. Duración (entre Progreso y Estado)
            dur_frame = ctk.CTkFrame(row, fg_color="transparent", width=cols_w[5], height=38)
            dur_frame.pack_propagate(False)
            dur_frame.pack(side="left", padx=6, pady=3)

            f_ini_obj = parsear_fecha_iso(fecha_ini)
            f_ter_obj = parsear_fecha_iso(fecha_ter or fecha_comp)

            if estado == "Por leer":
                ctk.CTkLabel(
                    dur_frame,
                    text="-",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#64748B"
                ).pack(expand=True)
            elif estado == "Leyendo":
                f_base = f_ini_obj or hoy
                dias = max(0, (hoy - f_base).days)
                txt_principal = "Hoy" if dias == 0 else f"{dias} día{'s' if dias != 1 else ''}"
                txt_secundario = f"Desde: {formatear_dd_mm_aaaa(f_base)}"

                ctk.CTkLabel(
                    dur_frame,
                    text=txt_principal,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#F59E0B",
                    height=15
                ).pack(anchor="center", pady=(3, 0))
                ctk.CTkLabel(
                    dur_frame,
                    text=txt_secundario,
                    font=ctk.CTkFont(size=9),
                    text_color="#94A3B8",
                    height=13
                ).pack(anchor="center")
            else:  # Completado
                f_fin = f_ter_obj or hoy
                f_comienzo = f_ini_obj or f_fin
                dias = max(0, (f_fin - f_comienzo).days)
                txt_principal = f"{dias} día{'s' if dias != 1 else ''}"
                txt_secundario = f"{formatear_dd_mm_aa(f_comienzo)} - {formatear_dd_mm_aa(f_fin)}"

                ctk.CTkLabel(
                    dur_frame,
                    text=txt_principal,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#10B981",
                    height=15
                ).pack(anchor="center", pady=(3, 0))
                ctk.CTkLabel(
                    dur_frame,
                    text=txt_secundario,
                    font=ctk.CTkFont(size=9),
                    text_color="#94A3B8",
                    height=13
                ).pack(anchor="center")

            # 6. Estado
            bg_c, text_c = badge_colors.get(estado, ("#1E293B", "#64748B"))
            badge = ctk.CTkLabel(row, text=estado, font=ctk.CTkFont(size=11, weight="bold"), text_color=text_c, fg_color=bg_c, corner_radius=12, width=cols_w[6], height=24)
            badge.pack(side="left", padx=6)

            # 7. Acción
            btn_gestionar = ctk.CTkButton(
                row,
                text="⚙️ Abrir",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=cols_w[7],
                height=26,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                command=lambda l=libro: self._abrir_modal(l)
            )
            btn_gestionar.pack(side="left", padx=6)

            # Hacer clic en cualquier parte de la fila (incluyendo sub-widgets de progreso y duración) abre el modal
            self._vincular_click_fila(row, libro, excluir=btn_gestionar)

    def _vincular_click_fila(self, widget, libro, excluir):
        if widget == excluir:
            return
        widget.bind("<Button-1>", lambda e, l=libro: self._abrir_modal(l))
        for child in widget.winfo_children():
            self._vincular_click_fila(child, libro, excluir)

    def _abrir_modal(self, libro_data):
        ModalGestionLibro(self, libro_data, on_update_callback=self.refrescar_datos)

    def _abrir_modal_nuevo(self):
        ModalNuevoLibro(self, on_create_callback=self.refrescar_datos)
