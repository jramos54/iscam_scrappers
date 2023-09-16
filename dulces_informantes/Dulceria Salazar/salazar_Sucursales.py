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
    INFORMANTE='Dulceria Salazar'
    URL='https://www.dulceriasalazar.com/pages/sucursales'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="main")

    sucursales_tags=main.find_all('h1')
    sucursales=[h1 for h1 in sucursales_tags if h1.get_text(strip=True)]
    sucursales.pop(0)
  
    directorio=[]
    direcciones=main.find_all(class_="SALvLe")

    telefonos_tags=main.find_all(class_="LrzXr zdqRlf kno-fv")
    telefonos=[tel for tel in telefonos_tags if tel.get_text(strip=True)]

    compresed=zip(sucursales,direcciones,telefonos)
    

    for sucursal in compresed:
        
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

        sucursal_texto=sucursal[0].text
        tienda['Sucursal']=sucursal_texto

        direccion_texto=sucursal[1].text.strip()
        direccion_lineas=direccion_texto.splitlines()
        for linea in direccion_lineas:
            if 'Dirección' in linea:
                tienda['Direccion']=linea[11:]

        tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
        
        longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
        tienda['Latitud'] = latitud
        tienda['Longitud'] = longitud

        tienda['Telefono']=sucursal[-1].text.strip()
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
    filename='salazar_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)