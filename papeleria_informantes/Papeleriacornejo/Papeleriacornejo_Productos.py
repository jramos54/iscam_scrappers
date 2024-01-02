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


def agregar_informacion(soup,informante,categoria,fecha):
    product_information = {
        'Informante': informante,
        'Categoria': categoria.strip(),
        'DescripcionCorta': '',
        'DescripcionLarga': '',
        'SKU': '',
        'Etiqueta': '',
        'Img': '',
        'Precio': '',
        'Fecha': fecha
        }
    container=soup.find(id="content")

    if container:
        descripcion_corta=container.find('h1')
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text

        descripcion_larga=container.find('div',class_="col-sm-4").find('li').text
        descripcion_tab=container.find(id="tab-description").text
        descripcion_larga_=descripcion_larga + ' .' + descripcion_tab
        if descripcion_larga:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']+'. '+descripcion_larga_

        sku=container.find('h3').text
        if sku:
            sku_=sku.split()
            product_information['SKU']=sku_[-1]

        imagen_element=container.find('div',class_="col-sm-8").find('li')
        imagen=imagen_element.find('a')
        if imagen:
            product_information['Img']=imagen.get('href')

        precio=container.find('div',class_="col-sm-4").find('h2')
        if precio:
            product_information['Precio']=precio.text.strip()

        # json_prod=json.dumps(product_information,indent=4)
        # print(json_prod)

    return product_information


def pagination(driver,link):
   
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('ul',class_="pagination")
    pages.append(link)

    if pagination_html:
        paginas=pagination_html.find_all('li')
        last_page_link=paginas[-1].find('a').get('href')
        last_page=int(last_page_link.split('=')[-1])
        
        for i in range(2,last_page+1):
            pages.append(link+'&page='+f'{i}')

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papeleria Cornejo'
    URL = 'https://www.papeleriacornejo.com/pc/index.php?route=common/home'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="menu")
    
    lista_level0=menu.find('ul')
    itemslevel0=lista_level0.find_all('li',recursive=False)

    counter=0
    for itemlevel0 in itemslevel0:
        
        # print(itemlevel0.find('a').text)
        # print('-'*40)
        
        lista_level1=itemlevel0.find('ul')
        if lista_level1:
            itemslevel1=lista_level1.find_all('li',recursive=False)
        else:
            continue
        
        for itemlevel1 in itemslevel1:
            # print(itemlevel1.find('a').text)
            # print('-  - '*10)
            categoria=itemlevel1.find('a').text
            link=itemlevel1.find('a').get('href')
            driver.get(link)
            page_html=BeautifulSoup(driver.page_source,'html.parser')
            body=page_html.find(id="content")
            itemslevel2=body.find_all('li')
            body_items=body.find_all('div',class_="caption")
            
            for itemlevel2 in itemslevel2:                
                categoria=itemlevel2.find('a').get_text()
                link=itemlevel2.find('a').get('href')
                print(categoria)
                # print(link)
                pages=pagination(driver,link)
                
                for page in pages:
                    driver.get(page)
                    page_html=BeautifulSoup(driver.page_source,'html.parser')

                    products=page_html.find_all('div',class_="caption")
                    for product in products:
                            
                        product_link=product.find('a')
                        # print(product_link.get('href'))
                        driver.get(product_link.get('href'))
                        
                        producto=agregar_informacion(
                            BeautifulSoup(driver.page_source, 'html.parser'),
                            INFORMANTE,categoria,fecha)
                        informacion.append(producto)
                        counter+=1
                        print(counter)
            
            for product in body_items:
                            
                        product_link=product.find('a')
                        # print(product_link.get('href'))
                        driver.get(product_link.get('href'))
                        
                        producto=agregar_informacion(
                            BeautifulSoup(driver.page_source, 'html.parser'),
                            INFORMANTE,categoria,fecha)
                        informacion.append(producto)
                        counter+=1
                        print(counter) 
    return informacion            
                

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
    chrome_options.add_argument("--ignore-certificate-errors")

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    driver_manager = ChromeDriverManager(path=driver_path)
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_papelera(driver,stamped_today)
    filename='Papeleriacornejo_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)

    # link='https://www.papeleriacornejo.com/pc/index.php?route=product/category&path=275_287_502'
    # for i in pagination(driver,link):
    #     response=requests.get(i)
    #     print(response.status_code)
    #     print(i)
    
    driver.quit()

    print(f"{time.time()-inicio}")

