"""SIGECI — Sistema Inteligente de Gestión de Correspondencia Institucional (ADEP).

Paquete principal de la aplicación Flask. Expone la fábrica create_app()
según el patrón Application Factory de Flask.
"""

import os
import sys
from werkzeug.utils import secure_filename

from flask import Flask, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (si existe)
load_dotenv()


def _verificar_variables_entorno():
    """Verifica que las variables de entorno críticas existan al arrancar."""
    faltantes = []
    for var in ["APP_USUARIO", "APP_CLAVE", "SECRET_KEY"]:
        if not os.environ.get(var):
            faltantes.append(var)
    if faltantes:
        print(f"Faltan variables de entorno: {', '.join(faltantes)}")
        sys.exit(1)


_verificar_variables_entorno()


def create_app():
    """Crea y configura la instancia de la aplicación Flask.

    Returns:
        Flask: aplicación configurada con blueprints de controladores.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Carpeta donde se almacenan los documentos adjuntos a los registros
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "archivos")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Extensiones permitidas para adjuntos de correspondencia
    ALLOWED_EXTENSIONS = {
        "pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp",
        "doc", "docx", "xls", "xlsx", "txt",
    }

    # Límite de subida: 16 MB por archivo
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        APP_NAME=os.environ.get("APP_NAME", "SIGECI"),
        ENV=os.environ.get("FLASK_ENV", "development"),
        DEBUG=os.environ.get("FLASK_DEBUG", "1") == "1",
        PERMANENT_SESSION_LIFETIME=8 * 3600,  # 8 horas
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        ALLOWED_EXTENSIONS=ALLOWED_EXTENSIONS,
        MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
    )

    # Registrar blueprints de controladores
    from app.controllers.main import main_bp

    app.register_blueprint(main_bp)

    @app.route("/health")
    def health():
        """Endpoint de salud para verificar que la app está en ejecución."""
        return jsonify({"status": "ok", "app": app.config["APP_NAME"]})

    return app
