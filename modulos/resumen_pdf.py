import os
import sys
import datetime
import customtkinter as ctk
from base_datos.conexion import obtener_conexion
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class ResumenPDFFrame(ctk.CTkFrame):
    """Vista para exportar resúmenes del reto a PDF."""

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
            text="📄 Exportar Resúmenes PDF",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Genera informes detallados de lecturas, métricas anuales y notas de aprendizaje",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8"
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(5, 0))

    def _crear_contenido(self):
        content_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=12, border_width=1, border_color="#1E293B")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        content_frame.grid_columnconfigure(0, weight=1)

        info_card = ctk.CTkFrame(content_frame, fg_color="#1E293B", corner_radius=10)
        info_card.pack(fill="x", padx=30, pady=30)

        ctk.CTkLabel(
            info_card,
            text="📑 Resumen Ejecutivo de Lecturas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            info_card,
            text="El documento PDF incluirá las estadísticas de avance global, el contador de libros completados "
                 "en el año en curso, la tabla detallada de libros y las notas clave registradas.",
            font=ctk.CTkFont(size=13),
            text_color="#CBD5E1",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        self.btn_exportar = ctk.CTkButton(
            content_frame,
            text="📥 Generar Reporte PDF",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=45,
            corner_radius=8,
            command=self.generar_pdf
        )
        self.btn_exportar.pack(padx=30, pady=10)

        self.lbl_estado = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#10B981"
        )
        self.lbl_estado.pack(padx=30, pady=10)

    def generar_pdf(self):
        try:
            pdf_filename = "Resumen_Capital_10.pdf"
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_path = os.path.join(base_dir, pdf_filename)

            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            story = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=22,
                leading=26,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=8
            )
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#64748B'),
                spaceAfter=14
            )
            kpi_style = ParagraphStyle(
                'KPIStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#1E293B'),
                spaceAfter=16
            )

            cell_header_left = ParagraphStyle(
                'CellHeaderLeft',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=12,
                textColor=colors.white
            )
            cell_header_center = ParagraphStyle(
                'CellHeaderCenter',
                parent=cell_header_left,
                alignment=1
            )
            cell_body_left = ParagraphStyle(
                'CellBodyLeft',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                leading=12,
                textColor=colors.HexColor('#0F172A')
            )
            cell_body_center = ParagraphStyle(
                'CellBodyCenter',
                parent=cell_body_left,
                alignment=1
            )

            story.append(Paragraph("Capital 10 - Reporte de Progreso y Resumen", title_style))
            story.append(Paragraph("Seguimiento Personalizado de Lectura e Inversión", subtitle_style))

            anio_actual = str(datetime.date.today().year)

            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT orden_reto, titulo, autor, categoria, total_paginas, paginas_leidas, estado, COALESCE(fecha_termino, fecha_completado) FROM libros ORDER BY orden_reto ASC;")
            libros = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM libros WHERE estado = 'Completado' AND strftime('%Y', COALESCE(fecha_termino, fecha_completado)) = ?;", (anio_actual,))
            leidos_anio = cursor.fetchone()[0] or 0
            conn.close()

            total_libros = len(libros)
            completados = sum(1 for r in libros if r[6] == "Completado")
            pag_leidas = sum(r[5] for r in libros)
            pag_totales = sum(r[4] for r in libros)
            porcentaje = int((pag_leidas / pag_totales) * 100) if pag_totales > 0 else 0

            resumen_texto = (
                f"Total Libros: {total_libros}   |   "
                f"Completados: {completados}/{total_libros}   |   "
                f"Leídos en {anio_actual}: {leidos_anio}   |   "
                f"Progreso Global: {porcentaje}% ({pag_leidas}/{pag_totales} págs.)"
            )
            story.append(Paragraph(resumen_texto, kpi_style))
            story.append(Spacer(1, 6))

            if not libros:
                story.append(Paragraph("No hay libros registrados actualmente en la base de datos.", cell_body_left))
            else:
                table_data = [[
                    Paragraph("#", cell_header_center),
                    Paragraph("Título", cell_header_left),
                    Paragraph("Autor", cell_header_left),
                    Paragraph("Categoría", cell_header_left),
                    Paragraph("Páginas", cell_header_center),
                    Paragraph("Estado", cell_header_center)
                ]]

                for row in libros:
                    estado_str = f"{row[6]} ({row[7][:4]})" if row[6] == "Completado" and row[7] else row[6]
                    table_data.append([
                        Paragraph(str(row[0]), cell_body_center),
                        Paragraph(row[1], cell_body_left),
                        Paragraph(row[2], cell_body_left),
                        Paragraph(row[3], cell_body_left),
                        Paragraph(f"{row[5]} / {row[4]}", cell_body_center),
                        Paragraph(estado_str, cell_body_center)
                    ])

                t = Table(table_data, colWidths=[25, 145, 115, 110, 70, 75])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
                ]))
                story.append(t)

            doc.build(story)

            self.lbl_estado.configure(
                text=f"✅ PDF generado exitosamente: {pdf_filename}",
                text_color="#10B981"
            )
        except Exception as e:
            self.lbl_estado.configure(
                text=f"❌ Error al generar PDF: {str(e)}",
                text_color="#EF4444"
            )
