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


def agregar_informacion(soup,informante,categoria,categoria_tipo,fecha):
    URL = 'https:'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Tipo':categoria_tipo,
        'Precio':'',
        'DescripcionLarga':'',
        'Maridaje':'',
        'AlcVol':'',
        'Marca':'',
        'PaisOrigen':'',
        'Uva':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha

        }
    container=soup.find(id="shopify-section-product-template")

    # sku=container.find('meta',itemprop="sku")
    # if sku:
    #     sku_float=float(sku.get('content'))
    #     sku_str=str(sku_float)
    #     product_information['SKU']=sku_str[:4]

    descripcion_corta=container.find('h1',itemprop="name")
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text
    time.sleep(1)

    # TIPO

    precio=container.find('span',class_="money")
    if precio:
        product_information['Precio']=precio.text.strip()
    time.sleep(1)

    descripcion_larga=container.find('div',itemprop="description")
    if descripcion_larga:
        product_information['DescripcionLarga']=descripcion_larga.text.strip().strip('\n').strip('\t')
    time.sleep(1)

    # MARIDAJE
    # ALCVOL
    # MARCA
    # PAIS ORIGEN
    # UVA
    # TAMANO
    if product_information['DescripcionCorta'] !='':
        words=product_information['DescripcionCorta'].split()
        product_information['Tamaño']=words[-1]
        product_information['Marca']=words[1]
    time.sleep(1)

    imagen=container.find('img')
    if imagen:
        imagen_link=URL+imagen.get('src')
        product_information['Img']=imagen_link
    time.sleep(1)

    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://laduenamx.com'
    
    driver.get(link)
    time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(id="shopify-section-collection-template")
    pagination_html=main_body.find('div',class_="pagination grid__item large--three-quarters push--large--one-quarter")
            
    if pagination_html:
        pages_urls=pagination_html.find_all('a')
        last_page=pages_urls[-2].get('href')[-1]
        for i in range(1,int(last_page)+1):
            page_link=link+f'?page={i}'
            pages.append(page_link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver, fecha):
    INFORMANTE = 'La Dueña'
    URL = 'https://laduenamx.com'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="top_links_wrapper")
    itemslevel0=menu.find('ul').find_all('li',recursive=False)
    counter=0
    for itemlevel0 in itemslevel0:
        categoria=itemlevel0.find('a').get_text().strip().strip('\n')
        menulevel1=itemlevel0.find('ul')

        if menulevel1:
            itemslevel1=menulevel1.find_all('li',recursive=False)
        else:
            itemslevel1=[itemlevel0]

        for itemlevel1 in itemslevel1:

            categoria_tipo=itemlevel1.find('a').get_text()
            print(categoria)
            link=URL+itemlevel1.find('a').get('href')

            pages=pagination(driver,link)

            for page in pages:
                driver.get(page)
                time.sleep(5)
                page_html=BeautifulSoup(driver.page_source,'html.parser')
                main_body=page_html.find(id="shopify-section-collection-template")
                product_section=main_body.find('div',class_="grid__item large--three-quarters collection-main-body")
                products=product_section.find_all('p',class_="product-grid--title")
                for product in products:
                    product_link=URL+product.find('a').get('href')
                    time.sleep(5)
                    driver.get(product_link)

            
                    producto=agregar_informacion(
                        BeautifulSoup(driver.page_source, 'html.parser'),
                        INFORMANTE,categoria,categoria_tipo,fecha)
                    
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

    driver_manager = ChromeDriverManager(path=driver_path)
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_vinos(driver,stamped_today)
    filename='laduena_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    # link='https://laduenamx.com/collections/vino-tinto'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

