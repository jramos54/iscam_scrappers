import threading,time, subprocess, traceback,json,concurrent.futures,os
import shutil

    
def execute_script(script,python_executable,destination):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name=os.path.join(script_dir, script['script_name'])
    try:
        print(f"Informante {script['informante']}")
        print(f"Se ejecuta {script['script_name']} ...")
        subprocess.check_call([python_executable, script_name,destination])
    except subprocess.CalledProcessError as e:
        print(f"Error en {script['script_name']}: {e}")
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error en {script['script_name']}:\n{traceback.format_exc()}\n\n")


def run_scripts(scripts, python_executable, max_threads):
    script_dir=os.path.dirname(os.path.abspath(__file__))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(execute_script, script, python_executable,os.path.join(script_dir,script['csvPath'])) for script in scripts]
        concurrent.futures.wait(futures)      

def run_scripts_one_by_one(scripts, python_executable):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for script in scripts:
        origin_path=os.path.join(script_dir, script['csvPath'])
        dest_path=os.path.join(origin_path, "obsoletos")
        mover_archivos(origin_path,dest_path)
        execute_script(script, python_executable, os.path.join(script_dir, script['csvPath']))
        
def mover_archivos(carpeta_origen, carpeta_destino):
    try:
        archivos = os.listdir(carpeta_origen)
        
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        
        for archivo in archivos:
            origen = os.path.join(carpeta_origen, archivo)
            destino = os.path.join(carpeta_destino, archivo)
            
            # Verifica si el elemento es un archivo antes de moverlo
            if os.path.isfile(origen):
                shutil.move(origen, destino)
        
        print(f"Archivos movidos de {carpeta_origen} a {carpeta_destino}")
    except Exception as e:
        print(f"Error al mover archivos: {str(e)}")
        
               
if __name__ == "__main__":
    with open('scripts.json','r',encoding='utf-8') as source:
        scripts = json.load(source)
        
    # max_threads=3
    python_executable=r'C:\Users\jramos\codingFiles\dacodes\scrapping_project_iscam\venv\Scripts\python.exe'
    
    run_scripts_one_by_one(scripts,python_executable)  
