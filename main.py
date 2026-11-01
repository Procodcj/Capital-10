import customtkinter as ctk
import sys
import os

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from base_datos.conexion import inicializar_db
from modulos.dashboard import DashboardFrame
from modulos.biblioteca import BibliotecaFrame
from modulos.notas import NotasFrame
from modulos.resumen_pdf import ResumenPDFFrame

# Configuración global de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

TEXTO_TERMINOS_LICENCIA = """TÉRMINOS DE USO Y DESLINDE DE RESPONSABILIDAD

Capital 10 es una herramienta diseñada para el registro, control y seguimiento personal de hábitos de lectura.

1. Uso "Tal cual" (AS IS):
Esta aplicación se proporciona de forma libre y gratuita, "tal cual" y según disponibilidad, sin garantías de ningún tipo, expresas o implícitas, incluyendo, entre otras, garantías de funcionamiento ininterrumpido, rendimiento, compatibilidad o ausencia de fallos técnicos.

2. Almacenamiento local y datos:
Toda la información se procesa y almacena localmente en el dispositivo del usuario a través de una base de datos SQLite. El usuario es el único responsable de la integridad y del respaldo periódico de sus archivos y registros. El desarrollador no asume responsabilidad alguna por pérdida accidental, corrupción de bases de datos o daño de información.

3. Limitación de responsabilidad:
En ningún caso el desarrollador (Procodcj) será responsable por daños directos, indirectos, incidentales, especiales o derivados que resulten del uso o la imposibilidad de uso de esta aplicación.

Al utilizar Capital 10, usted reconoce y acepta estos términos en su totalidad.

© 2026 Procodcj. Todos los derechos reservados."""


class ModalAcercaDe(ctk.CTkToplevel):
    """Ventana modal emergente con información de autoría, términos de uso y deslinde de responsabilidad."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Acerca de / Licencia - Capital 10")

        ancho, alto = 580, 500
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - ancho) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{max(0, x)}+{max(0, y)}")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")

        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.focus_set()

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Cabecera
        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)

        lbl_titulo = ctk.CTkLabel(
            header,
            text="Capital 10",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F8FAFC"
        )
        lbl_titulo.pack(anchor="center", padx=20, pady=(18, 2))

        lbl_autor = ctk.CTkLabel(
            header,
            text="Desarrollado por: Procodcj (GitHub)",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        lbl_autor.pack(anchor="center", padx=20, pady=(0, 16))

        # Área de texto de términos en modo sólo lectura
        txt_terminos = ctk.CTkTextbox(
            self,
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=10,
            text_color="#E2E8F0",
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        txt_terminos.pack(fill="both", expand=True, padx=24, pady=(18, 14))
        txt_terminos.insert("1.0", TEXTO_TERMINOS_LICENCIA)
        txt_terminos.configure(state="disabled")

        # Botón de cierre al pie del modal
        btn_cerrar = ctk.CTkButton(
            self,
            text="Entendido / Cerrar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=180,
            height=38,
            corner_radius=8,
            command=self.destroy
        )
        btn_cerrar.pack(pady=(0, 18))


class Capital10App(ctk.CTk):
    """Aplicación principal Capital 10 con navegación lateral."""

    def __init__(self):
        super().__init__()

        # Inicialización y migración automática de Base de Datos al arrancar
        inicializar_db()

        # Configuración de ventana principal
        self.title("Capital 10")
        self.geometry("1120x680")
        self.minsize(980, 600)

        # Configuración del grid principal (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Crear Barra Lateral (Sidebar)
        self._crear_sidebar()

        # 2. Área de Contenido Principal
        self.main_content_frame = ctk.CTkFrame(self, fg_color="#090D16", corner_radius=0)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Vistas de la aplicación
        self.vistas = {}
        self._inicializar_vistas()

        # Mostrar vista inicial (Dashboard)
        self.mostrar_vista("dashboard")

    def _crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0F172A")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        # Logo / Marca
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="💎 CAPITAL 10",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F8FAFC"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Gestión de Lectura",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 25))

        # Botones de navegación
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 Dashboard de Libros",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=lambda: self.mostrar_vista("dashboard")
        )
        self.btn_dashboard.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_biblioteca = ctk.CTkButton(
            self.sidebar_frame,
            text="📚 Biblioteca",
            anchor="w",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="transparent",
            text_color="#CBD5E1",
            hover_color="#1E293B",
            command=lambda: self.mostrar_vista("biblioteca")
        )
        self.btn_biblioteca.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_notas = ctk.CTkButton(
            self.sidebar_frame,
            text="📝 Notas de Lectura",
            anchor="w",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="transparent",
            text_color="#CBD5E1",
            hover_color="#1E293B",
            command=lambda: self.mostrar_vista("notas")
        )
        self.btn_notas.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_pdf = ctk.CTkButton(
            self.sidebar_frame,
            text="📄 Exportar Resúmenes PDF",
            anchor="w",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="transparent",
            text_color="#CBD5E1",
            hover_color="#1E293B",
            command=lambda: self.mostrar_vista("pdf")
        )
        self.btn_pdf.grid(row=5, column=0, padx=15, pady=8, sticky="ew")

        # Botón secundario en la parte inferior del menú lateral
        self.btn_acerca = ctk.CTkButton(
            self.sidebar_frame,
            text="⚖️ Acerca de / Licencia",
            font=ctk.CTkFont(size=12),
            height=32,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color="#1E293B",
            text_color="#94A3B8",
            hover_color="#1E293B",
            command=self._abrir_acerca_de
        )
        self.btn_acerca.grid(row=7, column=0, padx=18, pady=(10, 4), sticky="ew")

        # Footer sidebar
        self.version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="v2.0 • Edición Dinámica",
            font=ctk.CTkFont(size=11),
            text_color="#475569"
        )
        self.version_label.grid(row=8, column=0, padx=20, pady=(4, 18))

    def _abrir_acerca_de(self):
        ModalAcercaDe(self)

    def _inicializar_vistas(self):
        self.vistas["dashboard"] = DashboardFrame(self.main_content_frame)
        self.vistas["biblioteca"] = BibliotecaFrame(self.main_content_frame)
        self.vistas["notas"] = NotasFrame(self.main_content_frame)
        self.vistas["pdf"] = ResumenPDFFrame(self.main_content_frame)

        for vista in self.vistas.values():
            vista.grid(row=0, column=0, sticky="nsew")

    def mostrar_vista(self, nombre_vista):
        """Muestra la vista seleccionada, refresca sus datos y resalta el botón activo."""
        for vista in self.vistas.values():
            vista.grid_remove()

        if nombre_vista in self.vistas:
            vista_activa = self.vistas[nombre_vista]
            if hasattr(vista_activa, "refrescar_datos"):
                vista_activa.refrescar_datos()
            vista_activa.grid(row=0, column=0, sticky="nsew")

        botones = {
            "dashboard": self.btn_dashboard,
            "biblioteca": self.btn_biblioteca,
            "notas": self.btn_notas,
            "pdf": self.btn_pdf
        }

        for clave, btn in botones.items():
            if clave == nombre_vista:
                btn.configure(fg_color="#3B82F6", text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#CBD5E1", font=ctk.CTkFont(size=13))


if __name__ == "__main__":
    app = Capital10App()
    app.mainloop()
