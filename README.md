# Prototipo para la Detección de Fracturas de Antebrazo

Aplicación Streamlit que usa YOLO (Ultralytics) para detectar fracturas en radiografías y generar un informe médico en PDF.

## Requisitos
- Python 3.10+
- Windows (probado) y CPU

Instala dependencias:

```
pip install -r requirements.txt
```

## Ejecutar

```
streamlit run despliegue.py
```

## Estructura
- `despliegue.py`: UI Streamlit y flujo principal
- `pdf_template.py`: plantilla ReportLab para el PDF
- `styles.css`, `Logo.png`: recursos de UI
- `best.pt`: pesos del modelo YOLO

 

