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

def sucursales_dulces(driver,fecha):
    """
    Funcion para el informante central del culce
    """
    INFORMANTE='Central del Dulce'
    URL='https://centraldeldulce.com/'
    directorio=[]

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="bloque_sucursales")
    sucursales_container=main.find(id="mapas")

    sucursales=sucursales_container.find_all(id="mapas_izq")
    
    for sucursal in sucursales:
        
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
        text_title=sucursal.find('h1').text.strip()
        text_sucursal=sucursal.find('p').text.strip()
        
        tienda['Sucursal']=text_title

        
        direccion_lineas=text_sucursal.split('|')
        direccion=direccion_lineas[0].strip('"')
        dir_loc=direccion.find('Lunes')
        tienda['Direccion']= direccion[:dir_loc].strip()
        for linea in direccion_lineas:
            if 'Tel' in linea: 
                loc_tel=linea.find('Tel')           
                tienda['Telefono']=linea[loc_tel+4:].strip('"')

        tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
        
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

    os.environ["WDM_LOCAL"] = '1'
    os.environ["WDM_PATH"] = driver_path

    driver_manager = ChromeDriverManager().install()
    

    driver = webdriver.Chrome(service=Service(driver_manager), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    sucursal_datos=sucursales_dulces(driver,stamped_today)
    filename='central_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)