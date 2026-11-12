"""SIGECI — Sistema Inteligente de Gestión de Correspondencia Institucional (ADEP).

Paquete principal de la aplicación Flask. Expone la fábrica create_app()
según el patrón Application Factory de Flask.
"""

import os

from flask import Flask, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (si existe)
load_dotenv()


def create_app():
    """Crea y configura la instancia de la aplicación Flask.

    Returns:
        Flask: aplicación configurada con blueprints de controladores.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-cambiar-en-produccion"),
        APP_NAME=os.environ.get("APP_NAME", "SIGECI"),
        ENV=os.environ.get("FLASK_ENV", "development"),
        DEBUG=os.environ.get("FLASK_DEBUG", "1") == "1",
    )

    # Registrar blueprints de controladores
    from app.controllers.main import main_bp

    app.register_blueprint(main_bp)

    @app.route("/health")
    def health():
        """Endpoint de salud para verificar que la app está en ejecución."""
        return jsonify({"status": "ok", "app": app.config["APP_NAME"]})

    return app
