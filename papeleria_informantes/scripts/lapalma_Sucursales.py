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

def sucursales_superpapelera(driver,fecha):
    """
    
    """
    INFORMANTE = 'Super Papelera'
    URL = 'https://superpapelera.com.mx/sucursales/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu=soup.find(id='main')
    sitios=menu.find_all('h3',class_='elementor-heading-title elementor-size-medium')
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
            parent=sitio.parent.parent
            ubicacion=parent.find_next_sibling().text
            sucursal=sitio.text

            direccion=ubicacion.strip()

            if sucursal:
                tienda['Sucursal']=sucursal
            
            if direccion:
                if direccion[-5:].isdigit():
                    tienda['Direccion']=direccion[:-6]+' CP '+direccion[-5:]
                else:tienda['Direccion']=direccion
                tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
                
                longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
                tienda['Latitud'] = latitud
                tienda['Longitud'] = longitud

                json_dato=json.dumps(tienda,indent=4)
                print(json_dato)

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

    datos=sucursales_superpapelera(driver,stamped_today)
    filename='superpapelera_sucursales_'+stamped_today+'.csv'

    # json_datos=json.dumps(datos,indent=4)
    # print(json_datos)
    funciones.exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")
