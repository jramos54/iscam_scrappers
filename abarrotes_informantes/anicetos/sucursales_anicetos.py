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
from selenium.webdriver.common.by import By
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto

def sucursales_abarrotes(driver,fecha):
    """
    
    """
    caracteres_eliminar = ['-', '"']

    INFORMANTE='Los Anicetos'
    URL='https://losanicetos.mx/contacto/'
    driver.get(URL)
    time.sleep(5)
    
    radio_buttons = driver.find_elements(By.CLASS_NAME, "jet-radio-list__input")
    directorio=[]
    
    for radio_button in radio_buttons:
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
        print('click')
        driver.execute_script("arguments[0].click();", radio_button)
        
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        main=soup.find(id="content")
    
        sucursal_texto=main.find('div', {'data-id': 'fd78bf4'})
        if sucursal_texto:
            sucursal=sucursal_texto.text
            tienda['Sucursal']=sucursal.strip()

        direccion_texto=main.find('div',{'data-id':"585fa0b"})
        if direccion_texto:
            direccion=direccion_texto.text
            tienda['Direccion']=direccion.strip()

            tienda['CP']=funciones.obtencion_cp(tienda['Direccion'])
            
            longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

        telefono_texto=main.find('div',{"data-id":"59072d8"})
        if telefono_texto:
            telefono=telefono_texto.text
            tienda['Telefono']=telefono.strip()
        
        print(json.dumps(tienda,indent=4))    
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
    filename='anicetos_tiendas_'+stamped_today+'.csv'
    funciones.exportar_csv(sucursal_datos,filename)