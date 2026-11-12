"""Configuración de pytest para SIGECI — Entrega 10.

Inserta la raíz del proyecto en sys.path para que pytest pueda importar
el paquete ``app`` y define fixtures compartidas por las pruebas de
cifras de control y casos límite de AGENTS.md.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from app import create_app  # noqa: E402
import app.controllers.main as controlador  # noqa: E402
from app.services.reglas_negocio import MOVIMIENTOS_REGISTRADOS  # noqa: E402


@pytest.fixture
def app():
    """Aplicación Flask en modo pruebas (no escribe en disco)."""
    app = create_app()
    app.config["TESTING"] = True
    # Evita persistir app/data/documentos.json durante las pruebas.
    controlador._guardar_documentos = lambda: None
    return app


@pytest.fixture
def client(app):
    """Cliente de prueba de Flask."""
    return app.test_client()


@pytest.fixture
def datos_insumos():
    """Datos de las 4 hojas del Excel de insumos (solo lectura)."""
    from app.services.leer_insumos import leer_insumos  # noqa: E402

    return leer_insumos()


@pytest.fixture(autouse=True)
def reset_estado_app():
    """Reinicia DOCUMENTOS y MOVIMIENTOS_REGISTRADOS antes de cada prueba."""
    controlador.DOCUMENTOS.clear()
    controlador._semillar_desde_insumos()
    MOVIMIENTOS_REGISTRADOS.clear()
