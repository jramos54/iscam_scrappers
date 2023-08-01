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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def sucursales_marchand(driver,fecha):
    """
    Funcion para el informante ifp03, ADOSA
    """
    INFORMANTE = 'Marchand'
    URL = 'https://www.marchand.com.mx/store-finder'
    MAIN_URL='https://www.marchand.com.mx/'
    driver.get(URL)
    html = driver.page_source

    # soup = BeautifulSoup(html, 'html.parser')

    # menu=soup.find('div',class_="cs-overflow-card")

    # sitios=menu.find_all('a')
    directorio=[]
    wait = WebDriverWait(driver, 10)
    links = driver.find_elements(By.CSS_SELECTOR, ".cs-store-filter")


    for link in links:
        driver.execute_script("arguments[0].scrollIntoView(true);", link)
        link.click()
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        menu=soup.find('ol',class_="cx-list")
        print(menu)

    # for sitio in sitios:
        
    #     tienda={
    #         'Informante':INFORMANTE,
    #         'Sucursal':'',
    #         'Direccion':'',
    #         'CP':'',
    #         'Latitud':'',
    #         'Longitud':'',
    #         'fecha':fecha
    #     }

    #     link=MAIN_URL+sitio.get('href')
        
    #     driver.get(link)
    #     time.sleep(2)
    #     html = driver.page_source
    #     soup = BeautifulSoup(html, 'html.parser')

    #     main = soup.find('body')
    #     root=main.find('app-root')
        
    #     root_estados=root.find('cx-storefront')
    #     estados=root_estados.find('router-outlet')
    #     #contenido=estados.find('cx-page-slot')
        
    #     print(estados.next_sibling.find_next('cx-page-slot',class_="MiddleContent has-components"))

    #     lista=soup.find_next_all('ol')
    #     print(lista,end='\n\n\n')
    #     tiendas=lista.find_all('li')

    #     for tienda_ in tiendas:

    #         sucursal=tienda_.find('h2',class_="cs-name-sucursal")
    #         if sucursal:
    #             tienda['Sucursal']=sucursal.get_text()

    #         direccion=tienda_.find('div',class_="cs-title-direccion")
    #         if direccion:
    #             direccion_=direccion.get_text()
    #             tienda['Direccion']=direccion_.splitlines()[0]
    #             tienda['CP']=direccion_[-9:-4]
                
    #             longitud,latitud = funciones.geolocalizacion(tienda['Direccion'])
    #             tienda['Latitud'] = latitud
    #             tienda['Longitud'] = longitud

    #             directorio.append(tienda)

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

    datos=sucursales_marchand(driver,stamped_today)
    filename='marchand_productos_'+stamped_today+'.csv'

    json_datos=json.dumps(datos,indent=4)
    print(json_datos)
    #funciones.exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")
