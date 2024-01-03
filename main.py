import threading,time, subprocess, traceback,json,concurrent.futures

    
def execute_script(script_name,python_executable):
    
    try:
        print(f"Se ejecuta {script_name} ...")
        subprocess.check_call([python_executable, script_name])
    except subprocess.CalledProcessError as e:
        print(f"Error en {script_name}: {e}")
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error en {script_name}:\n{traceback.format_exc()}\n\n")


def run_scripts(scripts, python_executable, max_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(execute_script, script['script'], python_executable) for script in scripts]
        concurrent.futures.wait(futures)
        
# def run_scripts(scripts,python_executable):
#     threads = []
#     for script in scripts:
#         print(script['informante'])
#         thread = threading.Thread(target=execute_script, args=(script['script'], python_executable))
#         threads.append(thread)
#         thread.start()

#     for thread in threads:
#         thread.join()
        
        
if __name__ == "__main__":
    with open('scripts.json','r',encoding='utf-8') as source:
        scripts = json.load(source)
        
    # for script in scripts:
    #     print(json.dumps(script,indent=4))
    max_threads=3
    python_executable=r'C:\Users\jramos\codingFiles\dacodes\scrapping_project_iscam\venv\Scripts\python.exe'
    run_scripts(scripts,python_executable,max_threads)  
