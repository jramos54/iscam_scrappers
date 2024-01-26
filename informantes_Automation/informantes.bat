@echo off

set LOG_FILE=C:\Users\jramos\codingFiles\dacodes\scrapping_project_iscam\registro.log
call C:\Users\jramos\codingFiles\dacodes\scrapping_project_iscam\venv\Scripts\activate

rem Ejecuta el script Python dentro del entorno virtual
python main.py

rem Desactiva el entorno virtual de Python
deacdeactivate >> %LOG_FILE%tivate



