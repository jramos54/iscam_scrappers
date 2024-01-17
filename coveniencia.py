import threading,time, subprocess, traceback,json,concurrent.futures,os

    
def execute_script(script,python_executable,destination):
    
    try:
        print(f"Informante {script['informante']}")
        print(f"Se ejecuta {script['script_name']} ...")
        subprocess.check_call([python_executable, script['script_name'],destination])
    except subprocess.CalledProcessError as e:
        print(f"Error en {script['script_name']}: {e}")
        with open("conveniencia_log.txt", "a") as log_file:
            log_file.write(f"Error en {script['script_name']}:\n{traceback.format_exc()}\n\n")


def run_scripts(scripts, python_executable, max_threads):
    script_dir=os.path.dirname(os.path.abspath(__file__))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(execute_script, script, python_executable,os.path.join(script_dir,script['csvPath'])) for script in scripts]
        concurrent.futures.wait(futures)      
        
if __name__ == "__main__":
    with open('conveiencia.json','r',encoding='utf-8') as source:
        scripts = json.load(source)
        
    max_threads=3
    python_executable=r'C:\Users\jramos\codingFiles\dacodes\scrapping_project_iscam\venv\Scripts\python.exe'
    run_scripts(scripts,python_executable,max_threads)  
