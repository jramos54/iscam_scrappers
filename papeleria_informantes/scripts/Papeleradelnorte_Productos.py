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
    container=soup.find('section')
    descripcion_corta=container.find_all('h4')
    complemento=container.find('h5')
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta[1].text + ' ' + complemento.text

    descripcion_larga=soup.find('p',class_="text-justify")
    if descripcion_larga:
        product_information['DescripcionLarga']=descripcion_larga.text

    # form=soup.find('form',class_='form-inline')
    # sku=form.find('p')
    # if sku:
    #     product_information['SKU']=sku.text[4:].strip()

    imagen=soup.find('img',id="stand-product-img")
    if imagen:
        product_information['Img']=imagen.get('src')

    precio=soup.find('h2',class_='text-primary')
    if precio:
        product_information['Precio']=precio.text.strip()

    # json_prod=json.dumps(product_information,indent=4)
    # print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://www.papeleradelnorte.com.mx/'
    
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


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papelera del Norte'
    URL = 'https://www.papeleradelnorte.com.mx/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find('ul',class_='nav navbar-nav')
    itemslevel0=menu.find_all('li',recursive=False)

    counter=0
    for itemlevel0 in itemslevel0:
        
        #print(itemlevel0.find('a').get_text())
        #print('-'*40)
        
        menulevel1=itemlevel0.find('ul')
        itemslevel1=menulevel1.find_all('li',recursive=False)
        
        for itemlevel1 in itemslevel1:
            #print(itemlevel1.find('a').get_text())
            #print('-  - '*10)
            menulevel2=itemlevel1.find('ul')
            itemslevel2=menulevel2.find_all('li',recursive=False)
            
            for itemlevel2 in itemslevel2:
                print(itemlevel2.find('a').get_text())
                categoria=itemlevel2.find('a').get_text()
                link=itemlevel2.find('a').get('href')
                #print(link)
                #pages=pagination(driver,link)
                
                driver.get(link)
                page_html=BeautifulSoup(driver.page_source,'html.parser')

                products=page_html.find('div',class_="col-lg-8 col-sm-6").find_all('h4')
                for product in products:
                    
                    product_link=product.find('a')
                    #print(product_link.text)
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

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    driver_manager = ChromeDriverManager(path=driver_path,version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_papelera(driver,stamped_today)
    filename='Papeleradelnorte_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")

