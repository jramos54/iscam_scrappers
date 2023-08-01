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

def sucursales_sanfelipeescolar(driver,fecha):
    """
    Funcion para el informante ifp02, San Felipe Escolar
    """
    INFORMANTE='San Felipe Escolar'
    URL='https://online.sanfelipeescolar.com.mx/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    ids={"MENUDEO_ID":'05d14c0',
        "MAYOREO_ID":'7ba0184'}

    directorio=[]

    for id in ids.keys():
        data=soup.find('div', {'data-id': ids.get(id)})
        lineas=data.find_all('p')
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }
        direccion=''
        for i,linea in enumerate(lineas):
            
            if i==0:
                tienda['Sucursal']=linea.get_text()
            else:
                direccion+=linea.get_text()+'\n'

        tienda['Direccion']=direccion.splitlines()[0][9:]
        tienda['CP']=funciones.obtencion_cp(direccion)
        longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
        tienda['Latitud'] = latitud
        tienda['Longitud'] = longitud
        directorio.append(tienda)
    
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

    driver_manager = ChromeDriverManager(path=driver_path)
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    sucursal_datos=sucursales_sanfelipeescolar(driver,stamped_today)
    filename='sanfelipeescolar_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)

    for i in sucursal_datos:
        dato_json=json.dumps(i,indent=4)
        print(dato_json)