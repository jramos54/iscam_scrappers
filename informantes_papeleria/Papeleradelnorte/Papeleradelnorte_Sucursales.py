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

def sucursales_papelera(driver,fecha):
    """
    Funcion para el informante ifp03, ADOSA
    """
    INFORMANTE = 'Papelera del Norte'
    URL = 'https://www.papeleradelnorte.com.mx/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu=soup.find('div',id='modal-sucursales')
    sitios=menu.find('div',class_='list-group')
    directorio=[]

    # for i,j in enumerate(sitios):
    #     contenido=j.text
    #     datos=contenido.splitlines()
    #     if len(contenido)>1:

    #         print(f"{i}--{contenido.splitlines()}")
    #         contenido.strip('\n\n\n\n') 
    #         print(contenido)   

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

            ubicacion=sitio.text
            
            if len(ubicacion)>1:
                
                tiendas=ubicacion.splitlines()
                tiendas=tiendas[4:]
                sucursal=tiendas.pop(0)
                if sucursal:
                    tienda['Sucursal']=sucursal

                direccion=tiendas.pop(1)
                if direccion:
                    
                    tienda['Direccion']=direccion
                    tienda['CP']=funciones.obtencion_cp(direccion)
                    
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

    driver_manager = ChromeDriverManager(path=driver_path)
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=sucursales_papelera(driver,stamped_today)
    filename='papeleradelnorte_sucursales_'+stamped_today+'.csv'

    json_datos=json.dumps(datos,indent=4)
    print(json_datos)
    funciones.exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")
