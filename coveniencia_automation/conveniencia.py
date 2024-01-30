import subprocess
import traceback
import json
import os
import pandas as pd
import pyodbc
import shutil


def execute_script(script_name, python_executable, destination):
    try:
        print(f"Se ejecuta {script_name} ...")
        subprocess.check_call([python_executable, script_name, destination])
    except subprocess.CalledProcessError as e:
        print(f"Error en {script_name}:{e}")
        with open("conveniencia_log.txt", "a") as log_file:
            log_file.write(f"Error en {script_name}:\n{traceback.format_exc()}\n\n")

def run_scripts_one_by_one(scripts, python_executable):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for script in scripts:
        script_name=os.path.join(script_dir, script['script_name'])
        execute_script(script_name, python_executable, os.path.join(script_dir, script['csvPath']))

def cargar_datos_en_sqlserver(archivo_csv):
    try:
        df = pd.read_csv(os.path.join(directorio_archivos, archivo_csv), sep='|')

        df['Precio'] = df['Precio'].fillna("")

        df = df[df['DescripcionCorta'].notna() & (df['DescripcionCorta'] != '')]

        if 'Promocion' not in df.columns:
            df['Promocion'] = ''  
        else:
            df['Promocion'].fillna('', inplace=True)

        conn = pyodbc.connect(connection_string)

        for index, row in df.iterrows():
            informante = row['Informante']
            categoria = row['Categoria']
            descripcioncorta = row['DescripcionCorta']
            precio = row['Precio']
            promocion = row['Promocion']
            fecha = row['Fecha']

            cursor = conn.cursor()

            cursor.execute("INSERT INTO PreciosConveniencia (Informante, Categoria, DescripcionCorta, Precio, Promocion, Fecha) VALUES (?, ?, ?, ?, ?, ?)",
                           informante, categoria, descripcioncorta, precio, promocion, fecha)

            conn.commit()

            cursor.close()

        conn.close()
        print(f"Los datos del archivo {archivo_csv} se han cargado en SQL Server con éxito.")

    except Exception as e:
        print(f"Error al cargar los datos del archivo {archivo_csv} en SQL Server: {str(e)}")

def mover_archivos(carpeta_origen, carpeta_destino):
    try:
        archivos = os.listdir(carpeta_origen)
        
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        
        for archivo in archivos:
            origen = os.path.join(carpeta_origen, archivo)
            destino = os.path.join(carpeta_destino, archivo)
            shutil.move(origen, destino)
        
        print(f"Archivos movidos de {carpeta_origen} a {carpeta_destino}")
    except Exception as e:
        print(f"Error al mover archivos: {str(e)}")
        
        
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_name=os.path.join(script_dir, 'conveniencia.json')
    
    with open(source_name, 'r', encoding='utf-8') as source:
        scripts = json.load(source)

    python_executable = r'C:\Users\jramos\codingFiles\dacodes\scrapping_project_iscam\venv\Scripts\python.exe'
    run_scripts_one_by_one(scripts, python_executable)
    
    connection_string = "Driver={SQL Server Native Client 11.0};Server=CCAZR-PROC01\PROC_cirugias;Database=ScrapingTDC;Uid=UsrInovacion;Pwd=M4ryW1tch041123!;"

    directorio_archivos = os.path.join(script_dir, 'csv')
    archivos_csv = [archivo for archivo in os.listdir(directorio_archivos) if archivo.endswith(".csv")]
    
    for archivo_csv in archivos_csv:
        cargar_datos_en_sqlserver(archivo_csv)
        
    carpeta_origen = os.path.join(script_dir, 'csv')
    carpeta_destino = os.path.join(script_dir, 'csv_merge')

    mover_archivos(carpeta_origen, carpeta_destino)
    
