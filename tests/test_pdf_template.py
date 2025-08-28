import sys, os
import io
from datetime import datetime
from PIL import Image
import pytest

# 👇 Agregar automáticamente la carpeta raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pdf_template import MedicalReportTemplate


def make_temp_image(tmp_path, name="img.png", size=(200, 120), color=(200, 200, 200)):
    p = tmp_path / name
    img = Image.new("RGB", size, color)
    img.save(p)
    return str(p)


def test_generate_report_basic(tmp_path, monkeypatch):
    # Guardar la función original antes de parchar
    real_exists = os.path.exists
    monkeypatch.setattr(
        os.path, "exists",
        lambda p: False if isinstance(p, str) and p.endswith("Logo.png") else real_exists(p)
    )

    patient_data = {
        "nombre": "Juan Perez",
        "edad": "45",
        "genero": "Masculino",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "historia_limpia": "Dolor en muñeca derecha tras caída."
    }

    detection_data = {
        "detections": {"Fractura": 0.8, "Texto": 0.1, "Metal": 0.0},
        "diagnosis": "Fractura detectada",
        "finding_limpio": "Se identificó una fractura ósea con alta confianza.",
        "max_class": "Fractura",
        "max_confidence": 0.8,
    }

    img_path = make_temp_image(tmp_path, "original.png")
    result_path = make_temp_image(tmp_path, "resultado.png")

    template = MedicalReportTemplate()
    buffer = template.generate_report(
        patient_data,
        detection_data,
        {"img_path": img_path, "result_path": result_path}
    )

    # Validaciones
    assert isinstance(buffer, io.BytesIO)
    data = buffer.getvalue()
    assert len(data) > 1000  # tamaño mínimo razonable
    assert data.startswith(b"%PDF"), "El archivo generado debe ser un PDF válido"
