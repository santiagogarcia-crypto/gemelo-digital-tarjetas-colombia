# ==============================================================================
# GEMELO DIGITAL FINANCIERO (FDT) - MOTOR AVANZADO DE REPORTES PDF CUSTOMIZABLES
# Módulo: advanced_pdf_report_generator.py
# ==============================================================================

import os
import io
import pandas as pd
import numpy as np
import streamlit as st

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class FDTReportEngine:
    """
    Motor de generación de reportes PDF dinámicos y consolidados para el
    Gemelo Digital Financiero (FDT). Permite la integración cruzada de variables,
    evaluación del Triángulo del Marketing de Servicios y cumplimiento de la Rúbrica.
    """

    def __init__(self, data_dir="data", outputs_dir="outputs"):
        self.data_dir = data_dir
        self.outputs_dir = outputs_dir
        self._load_datasets()

    def _load_datasets(self):
        """Carga y consolida los datasets de los diferentes modelos del Gemelo Digital."""
        self.df_sfc = pd.DataFrame()
        self.df_const = pd.DataFrame()
        self.df_kmeans = pd.DataFrame()
        self.df_econ = pd.DataFrame()

        # 1. Cargar Serie Temporal SFC
        if os.path.exists(self.data_dir):
            csv_files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            if csv_files:
                self.df_sfc = pd.read_csv(csv_files[0])

        # 2. Cargar Constelación Financiera
        path_const = os.path.join(self.outputs_dir, "matriz_constelacion_financiera.csv")
        if os.path.exists(path_const):
            self.df_const = pd.read_csv(path_const)

        # 3. Cargar Segmentación K-Means
        path_kmeans = os.path.join(self.outputs_dir, "perfiles_clientes_gemelo.csv")
        if os.path.exists(path_kmeans):
            self.df_kmeans = pd.read_csv(path_kmeans)

        # 4. Cargar Modelo Econométrico
        path_econ = os.path.join(self.outputs_dir, "modelo_diferenciacion_econometrico.csv")
        if os.path.exists(path_econ):
            self.df_econ = pd.read_csv(path_econ)

    def calculate_cross_analytics(self, entidad_target=None):
        """
        Calcula métricas consolidadas y cruces dinámicos de variables entre los modelos:
        - Perfiles K-Means vs. Márgenes de Red Multilado.
        - Inelasticidad vs. Variación de Cuota de Mercado.
        - Tasa de Interés Promedio vs. Volumen Transado.
        """
        metrics = {
            "volumen_total_mercado": 0,
            "entidad_target": entidad_target or "Todas las Entidades",
            "volumen_entidad": 0,
            "cuota_mercado_entidad": 0.0,
            "margen_neto_red": 0,
            "mdr_promedio": 0.0,
            "cluster_dominante": "N/A",
            "ticket_promedio_cluster": 0,
            "inelasticidad_promedio": 0.0,
            "impacto_shock_cuota": 0.0,
            "cruce_cluster_margen": []
        }

        # Cruce SFC & Constelación
        if not self.df_const.empty:
            metrics["volumen_total_mercado"] = self.df_const.get("volumen_transado_mensual", pd.Series([0])).sum()
            metrics["margen_neto_red"] = self.df_const.get("margen_neto_operativo", pd.Series([0])).sum()
            
            if "ingreso_mdr_comercio" in self.df_const.columns and "volumen_transado_mensual" in self.df_const.columns:
                total_vol = self.df_const["volumen_transado_mensual"].sum()
                metrics["mdr_promedio"] = (self.df_const["ingreso_mdr_comercio"].sum() / total_vol * 100) if total_vol > 0 else 0.0

            if entidad_target and "nombreentidad" in self.df_const.columns:
                df_ent = self.df_const[self.df_const["nombreentidad"] == entidad_target]
                if not df_ent.empty:
                    metrics["volumen_entidad"] = df_ent["volumen_transado_mensual"].values[0]
                    metrics["cuota_mercado_entidad"] = (metrics["volumen_entidad"] / metrics["volumen_total_mercado"] * 100) if metrics["volumen_total_mercado"] > 0 else 0.0

        # Cruce K-Means Comportamental
        if not self.df_kmeans.empty:
            if entidad_target and "Entidad" in self.df_kmeans.columns:
                df_ent_k = self.df_kmeans[self.df_kmeans["Entidad"] == entidad_target]
                if not df_ent_k.empty:
                    metrics["cluster_dominante"] = df_ent_k.get("Nombre_Perfil", pd.Series(["N/A"])).values[0]
                    metrics["ticket_promedio_cluster"] = df_ent_k.get("Ticket_Promedio_COP", pd.Series([0])).values[0]
            else:
                metrics["cluster_dominante"] = self.df_kmeans.get("Nombre_Perfil", pd.Series(["General"])).mode()[0] if "Nombre_Perfil" in self.df_kmeans.columns else "Multiclúster"
                metrics["ticket_promedio_cluster"] = self.df_kmeans.get("Ticket_Promedio_COP", pd.Series([0])).mean()

        # Cruce Econométrico
        if not self.df_econ.empty:
            metrics["inelasticidad_promedio"] = self.df_econ.get("Inelasticidad_Cruzada", pd.Series([0])).mean()
            if entidad_target and "Entidad" in self.df_econ.columns:
                df_ent_e = self.df_econ[self.df_econ["Entidad"] == entidad_target]
                if not df_ent_e.empty:
                    metrics["impacto_shock_cuota"] = df_ent_e.get("Variacion_Absoluta_Cuota", pd.Series([0])).values[0]
            else:
                metrics["impacto_shock_cuota"] = self.df_econ.get("Variacion_Absoluta_Cuota", pd.Series([0])).mean()

        # Cruce de Variables: Clúster vs. Márgenes de Red
        if not self.df_kmeans.empty and not self.df_const.empty:
            col_ent_k = "Entidad" if "Entidad" in self.df_kmeans.columns else self.df_kmeans.columns[0]
            col_ent_c = "nombreentidad" if "nombreentidad" in self.df_const.columns else self.df_const.columns[0]
            
            merged = pd.merge(self.df_kmeans, self.df_const, left_on=col_ent_k, right_on=col_ent_c, how="inner")
            if "Nombre_Perfil" in merged.columns and "margen_neto_operativo" in merged.columns:
                grp = merged.groupby("Nombre_Perfil").agg({
                    "margen_neto_operativo": "sum",
                    "Ticket_Promedio_COP": "mean" if "Ticket_Promedio_COP" in merged.columns else "count"
                }).reset_index()
                
                metrics["cruce_cluster_margen"] = grp.to_dict(orient="records")

        return metrics

    def generate_pdf(
        self,
        filename,
        student_info,
        modules_selected,
        strategic_decisions,
        target_entity=None
    ):
        """
        Construye el PDF altamente personalizado utilizando ReportLab Flowables.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Estilos Personalizados
        primary_color = colors.HexColor("#0F172A")
        secondary_color = colors.HexColor("#2563EB")
        accent_color = colors.HexColor("#0284C7")
        bg_light = colors.HexColor("#F8FAFC")
        text_dark = colors.HexColor("#1E293B")

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=primary_color,
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=14
        )
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=secondary_color,
            spaceBefore=12,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=text_dark,
            spaceAfter=6
        )
        header_table_style = ParagraphStyle(
            'HeaderTableStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            textColor=colors.white
        )
        cell_table_style = ParagraphStyle(
            'CellTableStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=text_dark
        )

        story = []

        # Encurbezado Principal
        story.append(Paragraph("🏛️ GEMELO DIGITAL FINANCIERO (FDT) - CASO DE ESTUDIO", title_style))
        story.append(Paragraph("Reporte de Evaluación Gerencial y Simulación de Mercado de Tarjetas de Crédito", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceAfter=12))

        # Información del Estudiante
        metrics = self.calculate_cross_analytics(target_entity)

        student_data = [
            [
                Paragraph("<b>Estudiante / Gerente:</b>", body_style),
                Paragraph(student_info.get("nombre", "N/A"), body_style),
                Paragraph("<b>Programa / Curso:</b>", body_style),
                Paragraph(student_info.get("curso", "Gerencia de Servicios Financieros"), body_style)
            ],
            [
                Paragraph("<b>Entidad Objetivo:</b>", body_style),
                Paragraph(target_entity or "Perspectiva Consolidada", body_style),
                Paragraph("<b>Fecha de Generación:</b>", body_style),
                Paragraph(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"), body_style)
            ]
        ]
        t_student = Table(student_data, colWidths=[110, 160, 110, 160])
        t_student.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_light),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_student)
        story.append(Spacer(1, 10))

        # Módulo 1: Resumen y Métricas
        story.append(Paragraph("1. Consolidado de Métricas Cruzadas del Gemelo Digital", section_style))

        kpi_data = [
            [
                Paragraph("Métrica Consolidada", header_table_style),
                Paragraph("Valor Obtenido (FDT)", header_table_style),
                Paragraph("Interpretación Estratégica", header_table_style)
            ],
            [
                Paragraph("Volumen Total del Mercado", cell_table_style),
                Paragraph(f"${metrics['volumen_total_mercado']:,.0f} COP", cell_table_style),
                Paragraph("Escala agregada del sistema de tarjetas transadas.", cell_table_style)
            ],
            [
                Paragraph("Margen Neto Operativo Red", cell_table_style),
                Paragraph(f"${metrics['margen_neto_red']:,.0f} COP", cell_table_style),
                Paragraph("Suma de ingresos por Intereses + MDR + Cuotas de Manejo.", cell_table_style)
            ],
            [
                Paragraph("Comisión Comercio (MDR Promedio)", cell_table_style),
                Paragraph(f"{metrics['mdr_promedio']:.2f}%", cell_table_style),
                Paragraph("Tasa efectiva promedio cobrada al sector adquirente.", cell_table_style)
            ],
            [
                Paragraph("Clúster Comportamental Dominante", cell_table_style),
                Paragraph(str(metrics['cluster_dominante']), cell_table_style),
                Paragraph("Perfil de consumo predominante en el segmento objetivo.", cell_table_style)
            ],
            [
                Paragraph("Impacto Proyectado por Shock de Precio", cell_table_style),
                Paragraph(f"{metrics['impacto_shock_cuota']:+.3f}%", cell_table_style),
                Paragraph("Variación absoluta de cuota ante aumento del +1.5% en cuota de manejo.", cell_table_style)
            ]
        ]

        t_kpi = Table(kpi_data, colWidths=[150, 140, 250])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 10))

        # Módulos Opcionales
        if "Serie Temporal SFC" in modules_selected and not self.df_sfc.empty:
            story.append(Paragraph("2. Módulo de Ingesta e Inercia Temporal (SFC)", section_style))
            story.append(Paragraph(
                "Análisis de evolución histórica del volumen de plásticos y comportamiento temporal de las entidades seleccionadas.", body_style
            ))
            story.append(Spacer(1, 6))

        if "Constelación Financiera (Red Multilado)" in modules_selected and not self.df_const.empty:
            story.append(Paragraph("3. Módulo de Constelación Financiera y Plataforma Multilado", section_style))
            story.append(Paragraph(
                "Evaluación del flujo de ingresos entre el Banco Emisor, Adquirente, Franquicia y Comercio.", body_style
            ))
            story.append(Spacer(1, 6))

        if "Segmentación Comportamental (K-Means)" in modules_selected and metrics.get("cruce_cluster_margen"):
            story.append(Paragraph("4. Cruce de Segmentación Comportamental vs. Margen Operativo", section_style))
            cruce_rows = [
                [
                    Paragraph("Perfil Comportamental", header_table_style),
                    Paragraph("Ticket Promedio COP", header_table_style),
                    Paragraph("Margen Operativo Generado", header_table_style)
                ]
            ]
            for item in metrics["cruce_cluster_margen"]:
                cruce_rows.append([
                    Paragraph(str(item.get("Nombre_Perfil", "N/A")), cell_table_style),
                    Paragraph(f"${item.get('Ticket_Promedio_COP', 0):,.0f}", cell_table_style),
                    Paragraph(f"${item.get('margen_neto_operativo', 0):,.0f} COP", cell_table_style)
                ])

            t_cruce = Table(cruce_rows, colWidths=[180, 160, 200])
            t_cruce.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), accent_color),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(t_cruce)
            story.append(Spacer(1, 10))

        if "Modelo Econométrico de Diferenciación" in modules_selected and not self.df_econ.empty:
            story.append(Paragraph("5. Módulo Econométrico de Diferenciación e Inelasticidad", section_style))
            story.append(Paragraph(
                "Simulación de la respuesta de demanda (Inelasticidad Cruzada) ante modificaciones en cuotas de manejo.", body_style
            ))
            story.append(Spacer(1, 6))

        # Triángulo del Marketing
        story.append(Paragraph("6. Alineación en el Triángulo del Marketing de Servicios", section_style))
        triangle_data = [
            [
                Paragraph("Dimensión del Triángulo", header_table_style),
                Paragraph("Estrategia Formulada por el Estudiante", header_table_style),
                Paragraph("Soporte en el Gemelo Digital", header_table_style)
            ],
            [
                Paragraph("<b>Marketing Externo</b><br/><i>(Prometer)</i>", cell_table_style),
                Paragraph(strategic_decisions.get("mk_externo", "Alineación de promesa de valor."), cell_table_style),
                Paragraph("Respaldo con Segmentación K-Means.", cell_table_style)
            ],
            [
                Paragraph("<b>Marketing Interno</b><br/><i>(Formular)</i>", cell_table_style),
                Paragraph(strategic_decisions.get("mk_interno", "Optimización del margen neto."), cell_table_style),
                Paragraph("Respaldo con la Constelación Multilado.", cell_table_style)
            ],
            [
                Paragraph("<b>Marketing Interactivo</b><br/><i>(Cumplir)</i>", cell_table_style),
                Paragraph(strategic_decisions.get("mk_interactivo", "Garantizar disponibilidad."), cell_table_style),
                Paragraph("Respaldo con disponibilidad tecnológica.", cell_table_style)
            ]
        ]
        t_tri = Table(triangle_data, colWidths=[140, 220, 180])
        t_tri.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_tri)
        story.append(Spacer(1, 10))

        # Rúbrica
        story.append(Paragraph("7. Autoevaluación alineada con la Rúbrica en 4 Dimensiones", section_style))
        rubric_data = [
            [
                Paragraph("Dimensión de Evaluación", header_table_style),
                Paragraph("Pond.", header_table_style),
                Paragraph("Declaración y Sustentación del Estudiante", header_table_style)
            ],
            [
                Paragraph("<b>1. Rigor Ingesta SFC</b>", cell_table_style),
                Paragraph("25%", cell_table_style),
                Paragraph(strategic_decisions.get("rub_ingesta", "Analizado serie temporal."), cell_table_style)
            ],
            [
                Paragraph("<b>2. Red Multilado</b>", cell_table_style),
                Paragraph("25%", cell_table_style),
                Paragraph(strategic_decisions.get("rub_multilado", "Ponderado margen de red."), cell_table_style)
            ],
            [
                Paragraph("<b>3. Perfilamiento K-Means</b>", cell_table_style),
                Paragraph("25%", cell_table_style),
                Paragraph(strategic_decisions.get("rub_kmeans", "Hábitos por segmento."), cell_table_style)
            ],
            [
                Paragraph("<b>4. Sustentación Econométrica</b>", cell_table_style),
                Paragraph("25%", cell_table_style),
                Paragraph(strategic_decisions.get("rub_econ", "Evaluada inelasticidad cruzada."), cell_table_style)
            ]
        ]
        t_rub = Table(rubric_data, colWidths=[150, 40, 350])
        t_rub.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_rub)

        doc.build(story)
        buffer.seek(0)
        return buffer
