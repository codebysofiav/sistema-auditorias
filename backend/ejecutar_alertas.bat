@echo off
cd /d "%~dp0"
.\venv\Scripts\python.exe manage.py generar_alertas_vencimiento >> alertas.log 2>&1
