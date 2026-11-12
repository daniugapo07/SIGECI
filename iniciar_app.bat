@echo off
cd /d "%~dp0"

echo ====================================
echo  SIGECI - Sistema de Correspondencia
echo  Iniciando en http://localhost:5000
echo ====================================

:: Abrir el navegador en la URL de la app
start "" "http://localhost:5000"

:: Ejecutar la app Flask dentro del entorno gestionado por uv
uv run python wsgi.py
