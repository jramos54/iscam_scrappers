"""
Scripts para obtener las sucursales de los informantes
"""

import os
import datetime
import json
import time

# Importar Selenium webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def sucursales_optivosa(driver,fecha):
    """
    Funcion para el informante ifp01, OPTIVOSA
    """
    INFORMANTE='OPTIVOSA'
    URL='https://www.optivosa.com/papeleria.html'

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    table_1=soup.find('table')
    table_2=table_1.find('table')
    table_3=table_2.find('table')
    table_4=table_3.find('table')

    sucursales = table_4.find_all('span')
    directorio=[]
    flag_direccion=False
    flag_tienda=False
    tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }

    for sucursal in sucursales:
        

        if 'subTITULOSazul' in sucursal.get('class'):
            tienda['Sucursal']=sucursal.get_text()
            flag_tienda=True

                
        elif 'pie' in sucursal.get('class'):
            direccion=sucursal.get_text()
            direccion_lines=direccion.splitlines()
            if 'Tel' in direccion_lines[-1]:
                direccion_lines.pop()
            texto_filtrado = [texto.strip() for texto in direccion_lines if texto.strip()]
            tienda['Direccion']='. '.join(texto_filtrado)
            tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
            longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud
            if tienda['Direccion'] !='':

                flag_direccion=True

        if flag_tienda and flag_direccion:   
            directorio.append(tienda)
            tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }
            flag_direccion=False
            flag_tienda=False
                
    return directorio

if __name__=='__main__':
    inicio=time.time()
    # Obtener la ruta absoluta del directorio actual del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en segundo plano
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--log-level=3") # no mostar log

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    driver_manager = ChromeDriverManager(path=driver_path,version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    sucursal_datos=sucursales_optivosa(driver,stamped_today)
    filename='optivosa_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)
    for sucursal in sucursal_datos:
        sucursal_json=json.dumps(sucursal,indent=4)
        print(sucursal_json)