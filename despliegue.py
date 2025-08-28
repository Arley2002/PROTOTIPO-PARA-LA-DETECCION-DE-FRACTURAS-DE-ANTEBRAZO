import streamlit as st
from ultralytics import YOLO
import cv2
from PIL import Image
import numpy as np
import torch
import os
from datetime import datetime
import base64
from io import BytesIO
from reportlab.lib.units import inch
from pdf_template import MedicalReportTemplate

# Forzar uso de CPU
device = torch.device("cpu")

# Ruta del modelo
MODEL_PATH = r"D:\\DeteccionDeFracturas\\best.pt"

# Cargar modelo
try:
    model = YOLO(MODEL_PATH)
    model.to(device)
except Exception as e:
    st.error(f"❌ No se pudo cargar el modelo. Verifique la ruta: {MODEL_PATH}")
    st.stop()

# Función para convertir imagen a base64
def image_to_base64(image):
    """Convierte una imagen PIL a base64 para mostrarla en HTML"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Directorios
IMAGES_DIR = "imagenes_cargadas"
RESULTS_DIR = "resultados"
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configuración de la página
st.set_page_config(
    page_title="Fundacion Universitaria de Popayan",
    page_icon="🩺",
    layout="wide"
)

# Cargar CSS externo 
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Aplicar estilos CSS externos 
try:
    load_css('styles.css')
except FileNotFoundError:
    st.warning("Archivo styles.css no encontrado. Usando estilos por defecto.")

# Título principal con logo
try:
    # Cargar el logo
    logo_path = r"D:\DeteccionDeFracturas\Logo.png"
    if os.path.exists(logo_path):
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.image(logo_path, width=120)
        with col2:
            st.markdown('<div class="medical-header"><h1 style="color: #0d47a1; font-size: 24px; text-align: center;">🩺 PROTOTIPO PARA LA DETECCIÓN DE FRACTURAS DE ANTEBRAZO A PARTIR DEL ANÁLISIS DE IMÁGENES RADIOLÓGICAS, UTILIZANDO REDES NEURONALES CONVOLUCIONALES</h1><p style="color: #1565c0; text-align: center;">Herramienta de apoyo diagnóstico asistida por inteligencia artificial</p></div>', unsafe_allow_html=True)
        with col3:
            st.image(logo_path, width=120)
    else:
        st.markdown('<div class="medical-header"><h1 style="color: #0d47a1; font-size: 24px;">🩺 PROTOTIPO PARA LA DETECCIÓN DE FRACTURAS DE ANTEBRAZO A PARTIR DEL ANÁLISIS DE IMÁGENES RADIOLÓGICAS, UTILIZANDO REDES NEURONALES CONVOLUCIONALES</h1><p style="color: #1565c0;">Herramienta de apoyo diagnóstico asistida por inteligencia artificial</p></div>', unsafe_allow_html=True)
except Exception:
    st.markdown('<div class="medical-header"><h1 style="color: #0d47a1; font-size: 24px;">🩺 PROTOTIPO PARA LA DETECCIÓN DE FRACTURAS DE ANTEBRAZO A PARTIR DEL ANÁLISIS DE IMÁGENES RADIOLÓGICAS, UTILIZANDO REDES NEURONALES CONVOLUCIONALES</h1><p style="color: #1565c0;">Herramienta de apoyo diagnóstico asistida por inteligencia artificial</p></div>', unsafe_allow_html=True)

# Función para redimensionar imágenes manteniendo relación de aspecto
def resize_image(image, max_width=300):  # Reducido de 700 a 300
    width_percent = (max_width / float(image.size[0]))
    new_height = int((float(image.size[1]) * float(width_percent)))
    return image.resize((max_width, new_height), Image.Resampling.LANCZOS)

# Estado persistente
if 'image' not in st.session_state:
    st.session_state.image = None
if 'annotated_image' not in st.session_state:
    st.session_state.annotated_image = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'report_ready' not in st.session_state:
    st.session_state.report_ready = False
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'diagnosis' not in st.session_state:
    st.session_state.diagnosis = ""
if 'finding' not in st.session_state:
    st.session_state.finding = ""
if 'detections' not in st.session_state:
    st.session_state.detections = {"Fractura": 0.0, "Texto": 0.0, "Metal": 0.0}
if 'max_class' not in st.session_state:
    st.session_state.max_class = ""
if 'max_confidence' not in st.session_state:
    st.session_state.max_confidence = 0.0

# --- Paso 1: Cargar imagen ---/////////////////////////////////////////////////////////
st.header("1️⃣ Carga de Radiografía")
st.markdown("Suba una imagen para análisis. Formatos aceptados: JPG, PNG")

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.session_state.image = image

        # Mostrar imagen cargada junto con ajustes de visualización
        st.subheader("Imagen cargada")
        
        # Crear contenedor principal para mejor alineación
        main_container = st.container()

        with main_container:
            # Primera fila: Imágenes alineadas
            col1, col2 = st.columns([1, 1])
            
            with col1:
                resized_image = resize_image(image)
                # Imagen centrada 
                st.markdown(
                    f'<div style="display: flex; justify-content: center;">'
                    f'<img src="data:image/png;base64,{image_to_base64(resized_image)}" style="max-width: 100%; height: auto;">'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<p style="text-align: center;">Radiografía original</p>', unsafe_allow_html=True)
            
            with col2:
                # Función para ajustar brillo y contraste
                def adjust_brightness_contrast(image, brightness=0, contrast=0):
                    img_array = np.array(image)
                    if contrast != 0:
                        f = 131 * (contrast + 127) / (127 * (131 - contrast))
                        img_array = cv2.addWeighted(img_array, f, img_array, 0, 127 * (1 - f))
                    if brightness != 0:
                        img_array = cv2.add(img_array, brightness)
                    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

                # Siempre mostrar la imagen ajustada para mantener alineación
                adjusted_image = adjust_brightness_contrast(image, 0, 0)  # Inicialmente sin ajustes
                resized_adjusted = resize_image(adjusted_image)
                preview_placeholder = st.empty()
                
                # Mostrar imagen inicial
                preview_placeholder.markdown(
                    f'<div style="display: flex; justify-content: center;">'
                    f'<img src="data:image/png;base64,{image_to_base64(resized_adjusted)}" style="max-width: 100%; height: auto;">'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<p style="text-align: center;">Vista previa con ajustes</p>', unsafe_allow_html=True)
            
            # Segunda fila: Controles de ajuste
            st.markdown("**⚙️ Ajustes de visualización**")
            col1_ctrl, col2_ctrl = st.columns([1, 1])
            
            with col1_ctrl:
                brightness = st.slider("Brillo", -100, 100, 0, key="bright_1")
            
            with col2_ctrl:
                contrast = st.slider("Contraste", -50, 50, 0, key="contr_1")
            
            # Actualizar imagen de vista previa cuando cambian los controles
            if brightness != 0 or contrast != 0:
                adjusted_image = adjust_brightness_contrast(image, brightness, contrast)
                resized_adjusted = resize_image(adjusted_image)
                preview_placeholder.markdown(
                    f'<div style="display: flex; justify-content: center;">'
                    f'<img src="data:image/png;base64,{image_to_base64(resized_adjusted)}" style="max-width: 100%; height: auto;">'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.success(f"✅ Ajustes aplicados: Brillo {brightness:+d}, Contraste {contrast:+d}")
            else:
                # Si no hay ajustes, mantener la imagen original
                st.info("💡 Sin ajustes aplicados")

        # Guardar imagen original
        img_path = os.path.join(IMAGES_DIR, "radiografia.png")
        image.save(img_path)
        st.session_state.img_path = img_path

        # Botón para analizar
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            analyze_button = st.button("🔬 Iniciar Análisis", use_container_width=True, type="primary")
        
        # Área para mostrar resultados (siempre visible)
        results_placeholder = st.empty()
        
        if analyze_button:
            with results_placeholder.container():
                with st.spinner("Analizando imagen médica... Por favor espere."):
                    img_array = np.array(image)
                    results = model.predict(img_array, device="cpu", imgsz=640)
                    
                    # Dibujar resultados
                    annotated_img = results[0].plot()
                    annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
                    st.session_state.annotated_image = Image.fromarray(annotated_img)
                    st.session_state.results = results[0]
                    
                    # Guardar resultado
                    result_path = os.path.join(RESULTS_DIR, "resultado.png")
                    cv2.imwrite(result_path, cv2.cvtColor(np.array(st.session_state.annotated_image), cv2.COLOR_RGB2BGR))
                    st.session_state.result_path = result_path
                    
                    # Interpretar resultados
                    boxes = results[0].boxes
                    detections = {"Fractura": 0.0, "Texto": 0.0, "Metal": 0.0}

                    if len(boxes) > 0:
                        for box in boxes:
                            class_id = int(box.cls.item())
                            confidence = box.conf.item()
                            
                            # Mapear IDs de clase a nombres
                            class_names = {0: "Fractura", 2: "Texto", 1: "Metal"}
                            
                            if class_id in class_names:
                                class_name = class_names[class_id]
                                if confidence > detections[class_name]:
                                    detections[class_name] = confidence

                    # Encontrar la detección con mayor confianza
                    max_class = max(detections, key=detections.get)
                    max_confidence = detections[max_class]

                    # Actualizar el estado de la sesión
                    st.session_state.detections = detections
                    st.session_state.max_class = max_class
                    st.session_state.max_confidence = max_confidence

                    # Determinar diagnóstico - MODIFICADO para manejar múltiples detecciones incluyendo Metal con umbral más flexible
                    significant_detections = []
                    moderate_detections = []
                    
                    for class_name, confidence in detections.items():
                        if confidence > 0.5:  # Umbral alto de confianza
                            significant_detections.append((class_name, confidence))
                        elif confidence > 0.3:  # Umbral moderado para incluir detecciones relevantes
                            moderate_detections.append((class_name, confidence))
                    
                    # Combinar todas las detecciones relevantes
                    all_relevant_detections = significant_detections + moderate_detections
                    all_relevant_detections.sort(key=lambda x: x[1], reverse=True)
                    
                    if significant_detections:
                        # Si hay detecciones significativas
                        if len(all_relevant_detections) > 1:
                            detection_names = [det[0] for det in all_relevant_detections]
                            confidences = [f"{det[1]:.2f}" for det in all_relevant_detections]
                            
                            # Priorizar fractura en el diagnóstico
                            if "Fractura" in detection_names:
                                # Crear lista de otros elementos detectados
                                other_elements = [name for name in detection_names if name != "Fractura"]
                                if other_elements:
                                    # Formatear elementos adicionales
                                    if len(other_elements) == 1:
                                        st.session_state.diagnosis = f"Fractura y {other_elements[0].lower()} detectados"
                                    elif len(other_elements) == 2:
                                        st.session_state.diagnosis = f"Fractura, {other_elements[0].lower()} y {other_elements[1].lower()} detectados"
                                    else:
                                        st.session_state.diagnosis = f"Fractura y múltiples elementos detectados"
                                    
                                    st.session_state.finding = f"Se identificaron múltiples elementos: {', '.join([f'{name} ({conf})' for name, conf in zip(detection_names, confidences)])}. La fractura requiere evaluación clínica inmediata."
                                else:
                                    st.session_state.diagnosis = "Fractura detectada"
                                    st.session_state.finding = f"Se identificó una fractura ósea con una confianza del {detections['Fractura']:.2f}. Se recomienda evaluación clínica adicional."
                            else:
                                # Solo elementos no fractura (texto y/o metal)
                                if len(detection_names) == 2:
                                    st.session_state.diagnosis = f"{detection_names[0]} y {detection_names[1].lower()} detectados"
                                elif len(detection_names) == 3:
                                    st.session_state.diagnosis = f"{detection_names[0]}, {detection_names[1].lower()} y {detection_names[2].lower()} detectados"
                                else:
                                    st.session_state.diagnosis = "Múltiples elementos detectados"
                                st.session_state.finding = f"Se identificaron: {', '.join([f'{name} ({conf})' for name, conf in zip(detection_names, confidences)])}."
                            

                            # Usar la fractura como clase principal si está presente, si no la de mayor confianza
                            if "Fractura" in detection_names:
                                st.session_state.max_class = "Fractura"
                                st.session_state.max_confidence = detections["Fractura"]
                            else:
                                st.session_state.max_class = significant_detections[0][0]
                                st.session_state.max_confidence = significant_detections[0][1]
                        else:
                            # Solo una detección significativa
                            class_name, confidence = significant_detections[0]
                            st.session_state.max_class = class_name
                            st.session_state.max_confidence = confidence
                            
                            if class_name == "Fractura":
                                st.session_state.diagnosis = "Fractura detectada"
                                st.session_state.finding = f"Se identificó una fractura ósea con una confianza del {confidence:.2f}. Se recomienda evaluación clínica adicional."
                            elif class_name == "Metal":
                                st.session_state.diagnosis = "Metal detectado"
                                st.session_state.finding = f"Se identificó material metálico en la imagen con una confianza del {confidence:.2f}. Posible presencia de implantes o elementos metálicos."
                            else:
                                st.session_state.diagnosis = f"{class_name} detectado"
                                st.session_state.finding = f"Se identificó {class_name.lower()} en la imagen con una confianza del {confidence:.2f}."
                    else:
                        # Sin detecciones significativas
                        max_class = max(detections, key=detections.get)
                        max_confidence = detections[max_class]
                        st.session_state.max_class = max_class
                        st.session_state.max_confidence = max_confidence
                        st.session_state.diagnosis = "Hallazgo negativo"
                        st.session_state.finding = "No se detectaron fracturas ni anomalías significativas en la imagen analizada."
                    
                    st.session_state.report_ready = True
                
                # Mostrar resultados inmediatamente después del análisis
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.subheader("2️⃣ Resultado del Análisis")
                
                # Mostrar diagnóstico con estilo médico
                if st.session_state.max_confidence > 0.5:
                    if st.session_state.max_class == "Fractura":
                        st.markdown(f'<div class="diagnosis-positive"><h3>⚠️ {st.session_state.diagnosis}</h3></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="diagnosis-other"><h3>🔍 {st.session_state.diagnosis}</h3></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="diagnosis-negative"><h3>✅ {st.session_state.diagnosis}</h3></div>', unsafe_allow_html=True)
                
                # Mostrar detecciones de todas las clases
                st.markdown("**Detalles de detección:**")

                # Contenedor para centrar las métricas
                st.markdown(
                    """
                    <div style="display: flex; justify-content: center; gap: 30px; margin: 20px 0;">
                    """,
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(
                        f'<div style="text-align: center;">'
                        f'<div style="font-size: 16px; color: #666; margin-bottom: 8px;">Fractura</div>'
                        f'<div style="font-size: 24px; font-weight: bold; color: #2196F3;">{st.session_state.detections["Fractura"]:.2f}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        f'<div style="text-align: center;">'
                        f'<div style="font-size: 16px; color: #666; margin-bottom: 8px;">Texto</div>'
                        f'<div style="font-size: 24px; font-weight: bold; color: #2196F3;">{st.session_state.detections["Texto"]:.2f}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col3:
                    st.markdown(
                        f'<div style="text-align: center;">'
                        f'<div style="font-size: 16px; color: #666; margin-bottom: 8px;">Metal</div>'
                        f'<div style="font-size: 24px; font-weight: bold; color: #2196F3;">{st.session_state.detections["Metal"]:.2f}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)
                
                # Mostrar imágenes lado a lado
                col1, col2 = st.columns(2)
                with col1:
                    resized_original = resize_image(st.session_state.image)
                    # Imagen centrada 
                    st.markdown(
                        f'<div style="display: flex; justify-content: center;">'
                        f'<img src="data:image/png;base64,{image_to_base64(resized_original)}" style="max-width: 100%; height: auto;">'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown('<p style="text-align: center;">Imagen Original</p>', unsafe_allow_html=True)
                with col2:
                    resized_annotated = resize_image(st.session_state.annotated_image)
                    # Imagen centrada 
                    st.markdown(
                        f'<div style="display: flex; justify-content: center;">'
                        f'<img src="data:image/png;base64,{image_to_base64(resized_annotated)}" style="max-width: 100%; height: auto;">'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown('<p style="text-align: center;">Imagen Analizada</p>', unsafe_allow_html=True)
                
                st.markdown(f"<p style='line-height: 1.6;'>{st.session_state.finding}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Actualizar estado
                st.rerun()

# --- Paso 2: Resultados del analisis ---////////////////////////////////////////////////////////////////////////

        # Mostrar resultados si ya están listos
        if st.session_state.report_ready and st.session_state.annotated_image is not None:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.subheader("2️⃣ Resultado del Análisis")
            
            # Mostrar diagnóstico con estilo médico
            if st.session_state.max_confidence > 0.5:
                if st.session_state.max_class == "Fractura":
                    st.markdown(f'<div class="diagnosis-positive"><h3>⚠️ {st.session_state.diagnosis}</h3></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="diagnosis-other"><h3>🔍 {st.session_state.diagnosis}</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="diagnosis-negative"><h3>✅ {st.session_state.diagnosis}</h3></div>', unsafe_allow_html=True)
            
            # Mostrar detecciones de todas las clases
            st.markdown("**Detalles de detección:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Fractura", f"{st.session_state.detections['Fractura']:.2f}", 
                          delta=None, delta_color="normal")
            with col2:
                st.metric("Texto", f"{st.session_state.detections['Texto']:.2f}", 
                          delta=None, delta_color="normal")
            with col3:
                st.metric("Metal", f"{st.session_state.detections['Metal']:.2f}", 
                          delta=None, delta_color="normal")
            
            # Mostrar imágenes lado a lado
            col1, col2 = st.columns(2)
            with col1:
                resized_original = resize_image(st.session_state.image)
                # Imagen centrada
                st.markdown(
                    f'<div style="display: flex; justify-content: center;">'
                    f'<img src="data:image/png;base64,{image_to_base64(resized_original)}" style="max-width: 100%; height: auto;">'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<p style="text-align: center;">Imagen Original</p>', unsafe_allow_html=True)
            with col2:
                resized_annotated = resize_image(st.session_state.annotated_image)
                # Imagen centrada
                st.markdown(
                    f'<div style="display: flex; justify-content: center;">'
                    f'<img src="data:image/png;base64,{image_to_base64(resized_annotated)}" style="max-width: 100%; height: auto;">'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<p style="text-align: center;">Imagen Analizada</p>', unsafe_allow_html=True)
            
            st.markdown(f"<p style='line-height: 1.6;'>{st.session_state.finding}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al procesar la imagen: {str(e)}")

# --- Paso 3: Generar informe ---////////////////////////////////////////////////////////////////////////
if st.session_state.report_ready and st.session_state.annotated_image is not None:
    st.markdown('<h2 class="section-header">3️⃣ Generación de Informe Médico</h2>', unsafe_allow_html=True)
    st.markdown("Complete los datos del paciente para generar un informe listo para descargar.")

    # Formulario
    with st.form(key="informe_form"):
        st.subheader("Datos del Paciente")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            nombre = st.text_input("Nombre completo del paciente *", placeholder="Ej: Juan Pérez García")
        with col2:
            edad = st.text_input("Edad", placeholder="Ej: 45")
        
        col1, col2 = st.columns(2)
        with col1:
            genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
        with col2:
            fecha = st.text_input("Fecha de estudio", value=datetime.now().strftime("%d/%m/%Y"))
        
        st.subheader("Información Clínica")
        historia = st.text_area("Antecedentes y motivo de estudio", height=100, 
                               placeholder="Ej: Paciente acude por dolor en muñeca derecha tras caída hace 2 horas. Sin antecedentes de traumatismos recientes.")
        
        generar = st.form_submit_button("📄 Generar Informe Médico", use_container_width=True, type="primary")

        if generar:
            if not nombre:
                st.warning("⚠️ Por favor, ingrese el nombre completo del paciente.")
            else:
                try:
                    # Limpiar texto
                    nombre = " ".join(nombre.strip().split()).title()
                    edad = edad.strip()
                    historia_limpia = " ".join(historia.replace("\n", " ").split()) if historia.strip() else "Sin información clínica proporcionada."
                    finding_limpio = " ".join(st.session_state.finding.replace("\n", " ").split())
                    
                    # Preparar datos para el template
                    patient_data = {
                        'nombre': nombre,
                        'edad': edad,
                        'genero': genero,
                        'fecha': fecha,
                        'historia_limpia': historia_limpia
                    }
                    
                    detection_data = {
                        'detections': st.session_state.detections,
                        'diagnosis': st.session_state.diagnosis,
                        'finding_limpio': finding_limpio,
                        'max_class': st.session_state.max_class,
                        'max_confidence': st.session_state.max_confidence
                    }
                    
                    image_paths = {
                        'img_path': st.session_state.img_path,
                        'result_path': st.session_state.result_path
                    }
                    
                    # Generar PDF usando el template
                    template = MedicalReportTemplate()
                    buffer = template.generate_report(patient_data, detection_data, image_paths)
                    
                    # Guardar PDF
                    pdf_path = os.path.join(RESULTS_DIR, "informe_fractura.pdf")
                    with open(pdf_path, "wb") as f:
                        f.write(buffer.getvalue())
                    
                    st.session_state.pdf_path = pdf_path
                    st.success("✅ Informe médico profesional generado con éxito.")
                    st.info("📄 El botón de descarga está disponible más abajo.")

                except Exception as e:
                    st.error(f"❌ Error al generar el PDF: {str(e)}")
                    import traceback
                    st.error(f"Detalles: {traceback.format_exc()}")

    # Botón de descarga fuera del formulario
    if 'pdf_path' in st.session_state and st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        st.markdown("<br>", unsafe_allow_html=True)
        with open(st.session_state.pdf_path, "rb") as file:
            st.download_button(
                label="📥 Descargar Informe Médico (PDF)",
                data=file,
                file_name=f"Informe_Fractura_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

# --- Mensaje final ---
st.markdown("<br><br>", unsafe_allow_html=True)
if not st.session_state.image:
    st.markdown('<div style="text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">'
                '<h3>¿Cómo usar este sistema?</h3>'
                '<ol style="text-align: left; margin: 0 20px;">'
                '<li>Suba una radiografía en formato JPG o PNG</li>'
                '<li>Haga clic en "Iniciar Análisis de Fracturas"</li>'
                '<li>Revise los resultados del análisis</li>'
                '<li>Complete los datos del paciente y genere el informe</li>'
                '</ol>'
                '</div>', unsafe_allow_html=True)

# --- Reiniciar ---
if st.session_state.image or st.session_state.pdf_path:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reiniciar Análisis", use_container_width=True):
        # Limpiar estado
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()