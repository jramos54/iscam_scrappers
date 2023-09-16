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

    descripcion_corta=soup.find('h1',class_="page-title")
    if descripcion_corta:
        descripcion_corta_=descripcion_corta.get_text().splitlines()
        texto_descripcion=descripcion_corta_[-1].strip(' ').strip('"')
        product_information['DescripcionCorta']=texto_descripcion.replace('\\','')
    
    descripcion_larga=soup.find('table',class_="data table additional-attributes")
    if descripcion_larga:
        descripcion_larga_=descripcion_larga.get_text().splitlines()
        product_information['DescripcionLarga']=product_information['DescripcionCorta']+'. '.join(elemento for elemento in descripcion_larga_ if elemento.strip() != '')
    
    precio=soup.find('span',class_="price")
    if precio:
        product_information['Precio']=precio.get_text()
    
    sku=soup.find('div',class_="product attribute sku")
    if sku:
        sku_=sku.get_text().splitlines()
        product_information['SKU']=sku_[-1].strip(' ')
    
    imagen=soup.find('img',class_="fotorama__img")
    if imagen:
        product_information['Img']=imagen.get('src')

    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information

def pagination(driver,link):
    URL = 'https://www.adosa.com.mx/'
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('div',class_='pages')
    
    pages.append(link)

    if pagination_html:
        total_articles=soup.find('p',id="toolbar-amount")
        
        text_articles=total_articles.text
        text_pages=text_articles.split(' ')
        text_pages.pop()
        num_articles=int(text_pages[-1])
        total_pages=(num_articles//30)+1
        for i in range(2,total_pages+1):
            pages.append(link+'?p='+f'{i}')

        
    return tuple(set(pages))

def productos_adosa(driver, fecha):
    INFORMANTE = 'ADOSA'
    URL = 'https://www.adosa.com.mx/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="store.menu")
    items_level0=menu.find_all('li')
    
    counter=0
    for item_level0 in items_level0:
        #
        title=item_level0.find('a')
        # print(title.get('title'))

        menu_level1=item_level0.find('div',class_="item-content1 hidden-xs hidden-sm")                
        containers_level1 = menu_level1.find_all('div',recursive=False)

        for container_level1 in containers_level1:
            items_level1=container_level1.find_all('div',recursive=False)
            for item_level1 in items_level1:
                categoria=item_level1.find('a')
                containers_level2=item_level1.find_all('div',class_="item-content1 hidden-xs hidden-sm")
               
                if containers_level2:
                    for container_level2 in containers_level2:
                        items_level2=container_level2.find_next().find_all('div')
                        
                        for item_level2 in items_level2:
                            categoria=item_level2.find('a')
                            link_page=categoria.get('href')
                            #paginacion de la categoria
                            pages=pagination(driver,link_page)
                            print(categoria.get_text())
# Comienza la extraccion por producto
                            for page in pages:
                                driver.get(page)
                                html_source=driver.page_source
                                soup=BeautifulSoup(html_source,'html.parser')
                                products=soup.find_all('li',class_="item product product-item")
                                for product in products:
                                    link=product.find('a')
                                    driver.get(link.get('href'))
                                    dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria.get_text(),fecha)
                                    informacion.append(dato)
                                    counter+=1
                                    print(counter)
                else:
                    print(categoria.get('title'))
                    driver.get(categoria.get('href'))
                    link_page=categoria.get('href')
                    pages=pagination(driver,link_page)
# Comienza la extraccion por producto
                    for page in pages:
                        driver.get(page)
                        html_source=driver.page_source
                        soup=BeautifulSoup(html_source,'html.parser')
                        products=soup.find_all('li',class_="item product product-item")
                        for product in products:
                            link=product.find('a')
                            driver.get(link.get('href'))
                            dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria.get_text(),fecha)
                            informacion.append(dato)
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

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    driver_manager = ChromeDriverManager(path=driver_path,version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_adosa(driver,stamped_today)
    filename='adosa_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    # link='https://www.adosa.com.mx/papeleria.html'
    # for i in pagination(driver,link):
    #     response=requests.get(i)
    #     print(response.status_code)
    driver.quit()

    print(f"{time.time()-inicio}")

    