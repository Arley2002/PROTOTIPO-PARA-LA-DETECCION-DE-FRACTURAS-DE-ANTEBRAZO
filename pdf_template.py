from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from datetime import datetime
import os
import textwrap

class MedicalReportTemplate:
    # === Estilos PDF ===
    MEDICAL_BLUE = colors.Color(0.12, 0.27, 0.49)
    DARK_BLUE   = colors.Color(0.05, 0.16, 0.31)
    LIGHT_GRAY  = colors.Color(0.95, 0.95, 0.95)
    MEDIUM_GRAY = colors.Color(0.6, 0.6, 0.6)

    def __init__(self):
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Crear estilos profesionales para el PDF médico"""
        styles = getSampleStyleSheet()
        
        # Colores profesionales (atributos de clase)
        medical_blue = self.MEDICAL_BLUE
        dark_blue = self.DARK_BLUE
        light_gray = self.LIGHT_GRAY
        medium_gray = self.MEDIUM_GRAY
        
        # Título principal del informe
        styles.add(ParagraphStyle(
            name='MedicalTitle',
            fontSize=18,
            alignment=1,
            spaceAfter=15,
            textColor=medical_blue,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo del hospital
        styles.add(ParagraphStyle(
            name='HospitalSubtitle',
            fontSize=14,
            alignment=1,
            spaceAfter=8,
            textColor=dark_blue,
            fontName='Helvetica'
        ))
        
        # Encabezados de sección principales
        styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=14,
            spaceBefore=18,
            spaceAfter=8,
            textColor=medical_blue,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=medical_blue,
            borderPadding=5
        ))
        
        # Texto normal profesional
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leading=16,
            textColor=colors.black,
            fontName='Helvetica',
            wordWrap='CJK'
        ))
        
        # Texto de datos del paciente
        styles.add(ParagraphStyle(
            name='PatientData',
            fontSize=11,
            spaceAfter=4,
            leading=14,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Pie de página profesional
        styles.add(ParagraphStyle(
            name='Footer',
            fontSize=9,
            alignment=1,
            textColor=medium_gray,
            fontName='Helvetica-Oblique'
        ))
        
        # Título de página de imágenes
        styles.add(ParagraphStyle(
            name='ImagePageTitle',
            fontSize=16,
            alignment=1,
            spaceAfter=20,
            textColor=medical_blue,
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def _wrap_text(self, text, width=80):
        """Función para ajustar texto que es demasiado largo"""
        if not text:
            return text
            
        # Dividir el texto en líneas más cortas
        wrapped_lines = textwrap.fill(text, width=width)
        return wrapped_lines
    
    def _create_professional_header(self, story):
        """Crear encabezado profesional con logo y diseño médico"""
        logo_path = r"D:\DeteccionDeFracturas\Logo.png"
        
        # Crear tabla de encabezado profesional
        if os.path.exists(logo_path):
            header_data = [
                [
                    RLImage(logo_path, width=1*inch, height=1*inch),
                    [
                        Paragraph("INFORME MÉDICO RADIOLÓGICO", self.styles['MedicalTitle']),
                        Paragraph("DETECCIÓN DE FRACTURAS DE ANTEBRAZO", self.styles['HospitalSubtitle'])
                    ],
                    RLImage(logo_path, width=1*inch, height=1*inch)
                ]
            ]
            header_table = Table(header_data, colWidths=[1.2*inch, 4.6*inch, 1.2*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('ALIGN', (1,0), (1,0), 'CENTER'),
                ('ALIGN', (2,0), (2,0), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ]))
        else:
            header_data = [
                [
                    Paragraph("INFORME MÉDICO RADIOLÓGICO", self.styles['MedicalTitle']),
                ],
                [
                    Paragraph("DETECCIÓN DE FRACTURAS DE ANTEBRAZO", self.styles['HospitalSubtitle'])
                ]
            ]
            header_table = Table(header_data, colWidths=[7*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ]))
        
        story.append(header_table)
        
        # Línea separadora
        line_table = Table([['']]*1, colWidths=[7*inch], rowHeights=[0.05*inch])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), self.MEDICAL_BLUE),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 15))
    
    def _create_hospital_info(self, story, fecha):
        """Crear información institucional profesional"""
        hospital_data = [
            ["INSTITUCIÓN:", "Fundación Universitaria de Popayán - FUP"],
            ["DEPARTAMENTO:", "Diagnóstico por Imágenes Asistido por IA"],
            ["FECHA DEL ESTUDIO:", fecha],
            ["N° DE INFORME:", "FRAC-AI-" + datetime.now().strftime("%Y%m%d%H%M")],
            ["MODALIDAD:", "Radiografía Digital con Análisis por IA"]
        ]
        
        hospital_table = Table(hospital_data, colWidths=[2*inch, 4*inch])
        hospital_table.setStyle(TableStyle([
            ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 10),
            ('FONT', (1,0), (1,-1), 'Helvetica', 10),
            ('TEXTCOLOR', (0,0), (0,-1), self.MEDICAL_BLUE),
            ('TEXTCOLOR', (1,0), (1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.Color(0.98, 0.98, 0.98)]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.Color(0.8, 0.8, 0.8)),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(hospital_table)
        story.append(Spacer(1, 20))
    
    def _create_patient_data(self, story, nombre, edad, genero, fecha):
        """Crear sección profesional de datos del paciente"""
        story.append(Paragraph("DATOS DEL PACIENTE", self.styles['SectionHeader']))
        
        patient_data = [
            ["NOMBRE COMPLETO:", nombre.upper()],
            ["EDAD:", edad + " años"],
            ["GÉNERO:", genero],
            ["FECHA DEL ESTUDIO:", fecha]
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 11),
            ('FONT', (1,0), (1,-1), 'Helvetica', 11),
            ('TEXTCOLOR', (0,0), (0,-1), self.MEDICAL_BLUE),
            ('TEXTCOLOR', (1,0), (1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.Color(0.98, 0.98, 0.98)]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.Color(0.8, 0.8, 0.8)),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))
    
    def _create_clinical_history(self, story, historia_limpia):
        """Crear sección profesional de historia clínica"""
        if historia_limpia and historia_limpia != "Sin información clínica proporcionada.":
            story.append(Paragraph("ANTECEDENTES CLÍNICOS Y MOTIVO DEL ESTUDIO", self.styles['SectionHeader']))
            
            # Ajustar texto si es demasiado largo
            historia_ajustada = self._wrap_text(historia_limpia, width=100)
            
            # Marco para la historia clínica
            history_table = Table([[Paragraph(historia_ajustada, self.styles['CustomNormal'])]], colWidths=[6*inch])
            history_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('VALIGN', (0,0), (0,0), 'TOP'),
                ('BACKGROUND', (0,0), (0,0), colors.Color(0.98, 0.98, 0.98)),
                ('GRID', (0,0), (-1,-1), 1, colors.Color(0.8, 0.8, 0.8)),
                ('TOPPADDING', (0,0), (-1,-1), 12),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(history_table)
            story.append(Spacer(1, 20))
    
    def _create_images_page(self, story, img_path, result_path):
        """Crear página separada para las imágenes"""
        story.append(PageBreak())
        
        # Título de la página de imágenes
        story.append(Paragraph("IMAGENES RADIOLÓGICAS", self.styles['ImagePageTitle']))
        story.append(Spacer(1, 20))
        
        # Imágenes con mejor diseño
        img_width = 3.2*inch
        # Aumentar ligeramente el alto de las imágenes
        img_height = 3.5*inch
        
        # Tabla para las imágenes con descripcciones detalladas
        img_data = [
            [
                Paragraph("<b>IMAGEN RADIOGRÁFICA ORIGINAL</b>", self.styles['CustomNormal']),
                Paragraph("<b>IMAGEN CON ANÁLISIS DE IA</b>", self.styles['CustomNormal'])
            ],
            [
                RLImage(img_path, width=img_width, height=img_height),
                RLImage(result_path, width=img_width, height=img_height)
            ]
        ]
        
        images_table = Table(img_data, colWidths=[3.8*inch, 3.8*inch])
        images_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,0), 0),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,1), (-1,1), 10),
            ('BOTTOMPADDING', (0,1), (-1,1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(images_table)
        
        # Nota técnica
        story.append(Spacer(1, 30))
        technical_note = """
        <b>NOTA TÉCNICA:</b> Las imágenes mostradas han sido procesadas mediante algoritmos de inteligencia artificial 
        especializados en detección de fracturas óseas. El sistema utiliza redes neuronales convolucionales entrenadas 
        específicamente para el análisis de radiografías de antebrazo. Los resultados deben ser interpretados siempre 
        en conjunto con la evaluación clínica del profesional médico tratante.
        """
        
        note_table = Table([[Paragraph(technical_note, self.styles['CustomNormal'])]], colWidths=[7*inch])
        note_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (0,0), colors.Color(0.4, 0.4, 0.4)),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('VALIGN', (0,0), (0,0), 'TOP'),
            ('BACKGROUND', (0,0), (0,0), colors.Color(0.98, 0.98, 0.98)),
            ('GRID', (0,0), (-1,-1), 1, colors.Color(0.8, 0.8, 0.8)),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(note_table)
    
    def _create_footer(self, story):
        """Crear pie de página profesional"""
        story.append(Spacer(1, 30))
        
        footer_text = f"""
        <b>INFORME GENERADO AUTOMÁTICAMENTE</b><br/>
        Sistema de IA Médica - {datetime.now().strftime('%d de %B de %Y, %H:%M hrs')}<br/>
        <i>Este informe debe ser revisado y validado por un médico radiólogo antes de ser considerado como diagnóstico definitivo.<br/>
        La interpretación final debe considerar siempre el contexto clínico del paciente.</i>
        """
        
        footer_table = Table([[Paragraph(footer_text, self.styles['Footer'])]], colWidths=[6*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(footer_table)
    
    def generate_report(self, patient_data, detection_data, image_paths):
        """Generar reporte médico profesional simplificado"""
        # Crear buffer para PDF
        buffer = BytesIO()
        
        # Configurar documento con márgenes 
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenido del PDF
        story = []
        
        # Crear secciones básicas
        self._create_professional_header(story)
        self._create_hospital_info(story, patient_data['fecha'])
        self._create_patient_data(story, patient_data['nombre'], patient_data['edad'], 
                                 patient_data['genero'], patient_data['fecha'])
        self._create_clinical_history(story, patient_data['historia_limpia'])
        self._create_footer(story)
        
        # Página separada para imágenes
        self._create_images_page(story, image_paths['img_path'], image_paths['result_path'])
        
        # Construir PDF
        doc.build(story)
        
        return buffer