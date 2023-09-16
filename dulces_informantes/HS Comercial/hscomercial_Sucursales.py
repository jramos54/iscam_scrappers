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
    Funcion para el informante HS comercial
    """
    INFORMANTE='H.S. Comercial'
    URL='https://hscomercial.mx/sucursal2021/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="main")

    sucursales=main.find_all('div',class_="wp-block-media-text__content")
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
            'Telefono':'',
            'Email':'',
            'fecha':fecha
        }

        sucursal_texto=sucursal.text
        sucursal_lineas=sucursal_texto.splitlines()
        sucursal_lineas.pop(0)
        tienda['Sucursal']=sucursal_lineas.pop(0)

        for linea in sucursal_lineas:
            if '@' in linea:
                tienda['Email']=linea
            elif 'tel' in linea.lower():

                tienda['Telefono']=linea[6:]
            else:
                tienda['Direccion']+=linea + ' '

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
    filename='hscomercial_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)