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

def sucursales_abarrotes(driver,fecha):
    """
    Funcion para el informante HS comercial
    """
    INFORMANTE='Farmadepot'
    URL='https://farmadepot.com.mx/sucursales/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="Content")

    sucursales_tags=main.find_all('div',class_="team team_vertical")
    
    directorio=[]
    for sucursal in sucursales_tags:
        
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'Telefono':'',
            'Email':'',
            'fecha':fecha
        }

        sucursal_texto=sucursal.find('h4')
        if sucursal_texto:
            tienda['Sucursal']=sucursal_texto.text.strip()

        direccion_texto=sucursal.find(class_="desc")
        if direccion_texto:

            direccion_lineas=direccion_texto.text.splitlines()
           
            tienda['Direccion']=' '.join(direccion_lineas[:-3])

            tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
            
            longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

        telefono=sucursal.find(class_="phone")
        if telefono:
            tienda['Telefono']=telefono.text.strip()
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

    os.environ["WDM_LOCAL"] = '1'
    os.environ["WDM_PATH"] = driver_path

    driver_manager = ChromeDriverManager().install()
    

    driver = webdriver.Chrome(service=Service(driver_manager), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    sucursal_datos=sucursales_abarrotes(driver,stamped_today)
    filename='farmadepot_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)