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
    descripcion_corta=soup.find('h1',class_="crumb-title")
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.get_text()

    descripcion_larga=soup.find('div',class_="conte-tab-description")
    if descripcion_larga:
        product_information['DescripcionLarga']=descripcion_larga.text

    sku=soup.find('div',class_='sku')
    if sku:
        product_information['SKU']=sku.text[4:].strip()

    imagen_section=soup.find(class_="thumbs cx-desktop-imagenes is-initialized")
    if imagen_section:
        imagen=imagen_section.find('img')
        if imagen:
            product_information['Img']=imagen.get('src')

    precio=soup.find('div',class_='price')
    if precio:
        product_information['Precio']=precio.text.strip()

    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://www.marchand.com.mx/'
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('div',class_='cx-pagination')
    
    if pagination_html:
        pages_urls=pagination_html.find_all('a')
        if pages_urls:
            for page_url in pages_urls:
                pages.append(URL+page_url.get('href'))
        else:
            pages.append(link)

    return tuple(set(pages))


def productos_marchand(driver, fecha):
    INFORMANTE = 'Marchand'
    URL = 'https://www.marchand.com.mx/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find('div',class_='category-table-horizontal-up dropdown')
    category_menu=menu.find_next('div')
    
    itemslevel0=category_menu.find_next().find_all('nav',recursive=False)
    counter=0
    for itemlevel0 in itemslevel0:
        
        #print(itemlevel0.find('h5').get_text())
        #print('-'*40)
        menulevel1=itemlevel0.find('div',class_="wrapper")
        itemslevel1=menulevel1.find('div',class_="childs").find_all('nav',recursive=False)
        for itemlevel1 in itemslevel1:
            #print(itemlevel1.find('h5').get_text())
            #print('-  - '*10)
            menulevel2=itemlevel1.find('div',class_="wrapper")
            itemslevel2=menulevel2.find('div',class_="childs").find_all('nav',recursive=False)
            for itemlevel2 in itemslevel2:
                print(itemlevel2.find('h5').get_text())
                categoria=itemlevel2.find('h5').get_text()
                link=URL+itemlevel2.find('a').get('href')
                pages=pagination(driver,link)
                
                for page in pages:
                    #print(page)
                    driver.get(page)
                    page_html=BeautifulSoup(driver.page_source,'html.parser')
                    products=page_html.find_all('div',class_='conten-product')
                    for product in products:
                        
                        product_link=product.find('a')
                        driver.get(URL+product_link.get('href'))
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

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    driver_manager = ChromeDriverManager(path=driver_path,version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_marchand(driver,stamped_today)
    filename='marchand_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")

