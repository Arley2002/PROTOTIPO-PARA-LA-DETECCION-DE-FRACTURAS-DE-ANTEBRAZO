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
    def __init__(self):
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Crear estilos profesionales para el PDF médico"""
        styles = getSampleStyleSheet()
        
        # Colores profesionales médicos
        medical_blue = colors.Color(0.12, 0.27, 0.49)  # Azul médico profesional
        dark_blue = colors.Color(0.05, 0.16, 0.31)     # Azul oscuro
        light_gray = colors.Color(0.95, 0.95, 0.95)    # Gris claro
        medium_gray = colors.Color(0.6, 0.6, 0.6)      # Gris medio
        
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
        
        # Encabezados de subsección
        styles.add(ParagraphStyle(
            name='SubSectionHeader',
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            textColor=dark_blue,
            fontName='Helvetica-Bold'
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
            wordWrap='CJK'  # Añadido para permitir ajuste de texto
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
    
    def _add_diagnosis_style(self, max_class):
        """Añadir estilo de diagnóstico profesional basado en la clase detectada"""
        if max_class == "Fractura":
            # Rojo profesional para fractura
            diagnosis_color = colors.Color(0.8, 0.1, 0.1)
        elif max_class in ["Texto", "Metal"]:
            # Naranja profesional para otros hallazgos
            diagnosis_color = colors.Color(0.9, 0.5, 0.1)
        else:
            # Verde profesional para hallazgos negativos
            diagnosis_color = colors.Color(0.1, 0.6, 0.1)
        
        self.styles.add(ParagraphStyle(
            name='Diagnosis',
            fontSize=13,
            textColor=diagnosis_color,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leading=18
        ))
    
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
            ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.12, 0.27, 0.49)),
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
            ('TEXTCOLOR', (0,0), (0,-1), colors.Color(0.12, 0.27, 0.49)),
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
            ["FECHA DE NACIMIENTO:", "No especificado"],
            ["FECHA DEL ESTUDIO:", fecha]
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 11),
            ('FONT', (1,0), (1,-1), 'Helvetica', 11),
            ('TEXTCOLOR', (0,0), (0,-1), colors.Color(0.12, 0.27, 0.49)),
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
    
    def _create_analysis_results(self, story, detections):
        """Crear sección profesional de resultados del análisis"""
        story.append(Paragraph("RESULTADOS DEL ANÁLISIS POR INTELIGENCIA ARTIFICIAL", self.styles['SectionHeader']))
        
        # Tabla de detecciones con diseño profesional
        detection_data = [
            ["PARÁMETRO EVALUADO", "NIVEL DE CONFIANZA", "INTERPRETACIÓN"],
            ["Fractura Ósea", f"{detections['Fractura']:.3f}", self._get_confidence_interpretation(detections['Fractura'])],
            ["Texto en Imagen", f"{detections['Texto']:.3f}", self._get_confidence_interpretation(detections['Texto'])],
            ["Material Metálico", f"{detections['Metal']:.3f}", self._get_confidence_interpretation(detections['Metal'])]
        ]
        
        detection_table = Table(detection_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        detection_table.setStyle(TableStyle([
            # Encabezado
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.12, 0.27, 0.49)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            
            # Datos
            ('FONT', (0,1), (-1,-1), 'Helvetica', 10),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('ALIGN', (0,1), (0,-1), 'LEFT'),
            ('ALIGN', (1,1), (1,-1), 'CENTER'),
            ('ALIGN', (2,1), (2,-1), 'CENTER'),
            
            # Estilo general
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.Color(0.98, 0.98, 0.98)]),
            ('GRID', (0,0), (-1,-1), 1, colors.Color(0.6, 0.6, 0.6)),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(detection_table)
        story.append(Spacer(1, 15))
    
    def _get_confidence_interpretation(self, confidence):
        """Interpretar el nivel de confianza"""
        if confidence >= 0.8:
            return "MUY ALTO"
        elif confidence >= 0.6:
            return "ALTO"
        elif confidence >= 0.4:
            return "MODERADO"
        elif confidence >= 0.2:
            return "BAJO"
        else:
            return "MUY BAJO"
    
    def _create_diagnosis(self, story, diagnosis):
        """Crear sección profesional de diagnóstico"""
        story.append(Paragraph("DIAGNÓSTICO RADIOLÓGICO", self.styles['SectionHeader']))
        
        # Ajustar texto si es demasiado largo
        diagnosis_ajustado = self._wrap_text(diagnosis.upper(), width=80)
        
        # Marco para el diagnóstico
        diagnosis_table = Table([[Paragraph(diagnosis_ajustado, self.styles['Diagnosis'])]], colWidths=[6*inch])
        diagnosis_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            ('BACKGROUND', (0,0), (0,0), colors.Color(0.95, 0.95, 0.95)),
            ('GRID', (0,0), (-1,-1), 2, colors.Color(0.12, 0.27, 0.49)),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(diagnosis_table)
        story.append(Spacer(1, 15))
    
    def _create_findings(self, story, finding_limpio):
        """Crear sección profesional de hallazgos"""
        story.append(Paragraph("DESCRIPCIÓN DE HALLAZGOS", self.styles['SectionHeader']))
        
        # Ajustar texto si es demasiado largo
        finding_ajustado = self._wrap_text(finding_limpio, width=100)
        
        findings_table = Table([[Paragraph(finding_ajustado, self.styles['CustomNormal'])]], colWidths=[6*inch])
        findings_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (0,0), colors.black),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('VALIGN', (0,0), (0,0), 'TOP'),
            ('BACKGROUND', (0,0), (0,0), colors.Color(0.98, 0.98, 0.98)),
            ('GRID', (0,0), (-1,-1), 1, colors.Color(0.8, 0.8, 0.8)),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(findings_table)
        story.append(Spacer(1, 20))
    
    def _create_conclusion(self, story, max_class, max_confidence):
        """Crear sección profesional de conclusión"""
        story.append(Paragraph("CONCLUSIÓN MÉDICA", self.styles['SectionHeader']))
        
        if max_confidence > 0.5:
            if max_class == "Fractura":
                conclusion = f"Se identifica evidencia radiológica compatible con fractura ósea (confianza: {max_confidence:.3f}). Se recomienda evaluación clínica inmediata y seguimiento ortopédico especializado."
            else:
                conclusion = f"Se identifica {max_class.lower()} en la imagen radiológica (confianza: {max_confidence:.3f}). Se recomienda correlación clínica y evaluación médica adicional según criterio facultativo."
        else:
            conclusion = "El análisis radiológico asistido por inteligencia artificial no identifica signos evidentes de fractura ósea. Los hallazgos son compatibles con estudio negativo para fractura en el segmento anatómico evaluado."
        
        # Ajustar texto si es demasiado largo
        conclusion_ajustada = self._wrap_text(conclusion, width=100)
        
        conclusion_table = Table([[Paragraph(conclusion_ajustada, self.styles['CustomNormal'])]], colWidths=[6*inch])
        conclusion_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (0,0), colors.black),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('VALIGN', (0,0), (0,0), 'TOP'),
            ('BACKGROUND', (0,0), (0,0), colors.Color(0.95, 0.98, 1.0)),
            ('GRID', (0,0), (-1,-1), 1, colors.Color(0.12, 0.27, 0.49)),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(conclusion_table)
    
    def _create_images_page(self, story, img_path, result_path):
        """Crear página separada para las imágenes"""
        story.append(PageBreak())
        
        # Título de la página de imágenes
        story.append(Paragraph("DOCUMENTACIÓN RADIOLÓGICA", self.styles['ImagePageTitle']))
        story.append(Spacer(1, 20))
        
        # Imágenes con mejor diseño
        img_width = 3.8*inch
        img_height = 3*inch
        
        # Tabla para las imágenes con descripcciones detalladas
        img_data = [
            [
                Paragraph("<b>IMAGEN RADIOGRÁFICA ORIGINAL</b>", self.styles['SubSectionHeader']),
                Paragraph("<b>IMAGEN CON ANÁLISIS DE IA</b>", self.styles['SubSectionHeader'])
            ],
            [
                RLImage(img_path, width=img_width, height=img_height),
                RLImage(result_path, width=img_width, height=img_height)
            ],
            [
                Paragraph("Radiografía digital original sin procesamiento. Imagen adquirida según protocolos estándar de radiología.", self.styles['CustomNormal']),
                Paragraph("Imagen procesada con sistema de inteligencia artificial para detección automática de fracturas. Las áreas de interés están destacadas según el análisis algorítmico.", self.styles['CustomNormal'])
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
            ('TOPPADDING', (0,2), (-1,2), 10),
            ('BOTTOMPADDING', (0,2), (-1,2), 0),
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
        """Generar reporte médico profesional completo"""
        # Añadir estilo de diagnóstico
        self._add_diagnosis_style(detection_data['max_class'])
        
        # Crear buffer para PDF
        buffer = BytesIO()
        
        # Configurar documento con márgenes profesionales
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
        
        # Crear todas las secciones
        self._create_professional_header(story)
        self._create_hospital_info(story, patient_data['fecha'])
        self._create_patient_data(story, patient_data['nombre'], patient_data['edad'], 
                                 patient_data['genero'], patient_data['fecha'])
        self._create_clinical_history(story, patient_data['historia_limpia'])
        self._create_analysis_results(story, detection_data['detections'])
        self._create_diagnosis(story, detection_data['diagnosis'])
        self._create_findings(story, detection_data['finding_limpio'])
        self._create_conclusion(story, detection_data['max_class'], detection_data['max_confidence'])
        self._create_footer(story)
        
        # Página separada para imágenes
        self._create_images_page(story, image_paths['img_path'], image_paths['result_path'])
        
        # Construir PDF
        doc.build(story)
        
        return buffer