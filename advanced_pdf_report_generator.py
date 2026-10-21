# ==============================================================================
# GEMELO DIGITAL FINANCIERO: MOTOR AVANZADO DE GENERACIÓN DE REPORTES PDF
# ==============================================================================

import os
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class FDTReportEngine:
    """Motor encargado de consolidar métricas y estructurar el reporte PDF de evaluación."""
    
    def __init__(self, data_dir, outputs_dir):
        self.data_dir = data_dir
        self.outputs_dir = outputs_dir
        
        # Carga de datasets de apoyo
        path_const = os.path.join(outputs_dir, "matriz_constelacion_financiera.csv")
        if os.path.exists(path_const):
            self.df_const = pd.read_csv(path_const)
        else:
            self.df_const = pd.DataFrame()

    def generate_pdf(self, filename="Reporte_Evaluacion_FDT.pdf", student_info=None, modules_selected=None, strategic_decisions=None, target_entity=None):
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
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1B365D'),
            spaceAfter=8
        )
        
        sub_style = ParagraphStyle(
            'DocSub',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=15
        )

        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#2D3748'),
            spaceAfter=10
        )

        h2_style = ParagraphStyle(
            'DocH2',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#1B365D'),
            spaceBefore=10,
            spaceAfter=6
        )

        story = []

        # Encabezado principal
        story.append(Paragraph("🏛️ Gemelo Digital Financiero - Reporte de Evaluación", title_style))
        
        nombre = student_info.get("nombre", "N/A") if student_info else "N/A"
        curso = student_info.get("curso", "N/A") if student_info else "N/A"
        entidad = target_entity if target_entity else "Perspectiva Consolidada"
        
        story.append(Paragraph(f"<b>Estudiante:</b> {nombre} | <b>Asignatura:</b> {curso} | <b>Enfoque:</b> {entidad}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=15))

        # Resumen Ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo del Modelo", h2_style))
        story.append(Paragraph(
            f"El presente reporte consolida los hallazgos cuantitativos del Gemelo Digital Financiero aplicados al mercado de tarjetas de crédito en Colombia. "
            f"Análisis enfocado en la entidad: <b>{entidad}</b>.",
            body_style
        ))

        # Módulos seleccionados
        if modules_selected:
            story.append(Paragraph("2. Módulos Evaluados", h2_style))
            mod_data = [["Módulo Analítico", "Estado de Evaluación"]]
            for mod in modules_selected:
                mod_data.append([mod, "Incluido en Simulación"])
            
            t = Table(mod_data, colWidths=[300, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1B365D')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0'))
            ]))
            story.append(t)
            story.append(Spacer(1, 15))

        # Decisiones Estratégicas
        if strategic_decisions:
            story.append(Paragraph("3. Lineamientos y Decisiones Estratégicas", h2_style))
            dec_data = [["Dimensión Estratégica", "Estrategia Formulada"]]
            for k, v in strategic_decisions.items():
                dec_data.append([k.replace('_', ' ').title(), v])
            
            t_dec = Table(dec_data, colWidths=[180, 320])
            t_dec.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))
            ]))
            story.append(t_dec)

        doc.build(story)
        buffer.seek(0)
        return buffer
