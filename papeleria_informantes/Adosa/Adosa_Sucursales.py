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

def sucursales_adosa(driver,fecha):
    """
    Funcion para el informante ifp03, ADOSA
    """
    INFORMANTE='ADOSA'
    URL='https://www.adosa.com.mx/sucursales'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find('main')

    sucursales=main.find_all('div',class_="pagebuilder-column")
    directorio=[]

    print(len(sucursales))

    for sucursal in sucursales:
        
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }

        nombre=sucursal.find(attrs={"data-content-type": "heading"})
        if nombre:
            tienda['Sucursal']=nombre.get_text()
        direccion=sucursal.find(attrs={"data-content-type": "text"})
        if direccion:
            direccion_=direccion.get_text()
            tienda['Direccion']=direccion_.splitlines()[0]
            tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
            directorio.append(tienda)
            longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

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

    sucursal_datos=sucursales_adosa(driver,stamped_today)
    filename='adosa_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)