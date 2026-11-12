"""Punto de entrada WSGI de la aplicación SIGECI.

Permite ejecutar la app directamente con `python wsgi.py` o a través de
un servidor WSGI (gunicorn, waitress, etc.) importando la variable `app`.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
