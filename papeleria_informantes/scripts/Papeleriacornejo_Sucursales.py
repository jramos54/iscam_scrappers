"""
Scripts para obtener los productos de los informantes
"""
import os
import datetime
import json
import time
import requests

# Importar Selenium webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def sucursales_cornejo(driver,fecha):
    """
    
    """
    INFORMANTE = 'Papeleria Cornejo'
    URL = 'https://www.papeleriacornejo.com/pc/index.php?route=information/contact'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu=soup.find(id="content")
    sitios=menu.find_all('div',class_='row')
    directorio=[]
   
    for sitio in sitios:
        
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }

        if sitio:
            ubicacion=sitio.find('address').text
            sucursal=sitio.find('strong')

            direccion=ubicacion.strip().splitlines()
            if sucursal:
                tienda['Sucursal']=sucursal.text
            
            if direccion:
                tienda['Direccion']='. '.join(elemento for elemento in direccion if '@' not in elemento)
                tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
                
                longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
                tienda['Latitud'] = latitud
                tienda['Longitud'] = longitud

                # json_dato=json.dumps(tienda,indent=4)
                # print(json_dato)

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

    driver_manager = ChromeDriverManager(path=driver_path,version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=sucursales_cornejo(driver,stamped_today)
    filename='Papeleriacornejo_sucursales_'+stamped_today+'.csv'

    # json_datos=json.dumps(datos,indent=4)
    # print(json_datos)
    funciones.exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")
