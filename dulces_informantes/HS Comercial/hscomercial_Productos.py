"""
Scripts para obtener los productos de los informantes
"""
import os
import datetime
import json
import time
import requests
import re

# Importar Selenium webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def text_segments(texto,word):
    segmentos_encontrados = []
    text=texto.lower()
    inicio = 0
    alc_pos = text.find(word, inicio)

    while alc_pos != -1:
        # Buscar la posición del próximo "alc" a partir de la posición después de la última ocurrencia
        siguiente_alc_pos = text.find(word, alc_pos + 1)

        # Si no se encuentra más "alc", tomar el resto del texto
        if siguiente_alc_pos == -1:
            segmento = text[alc_pos:]
        else:
            segmento = text[alc_pos:siguiente_alc_pos]

        segmentos_encontrados.append(segmento.strip())
        inicio = alc_pos + 1
        alc_pos = text.find(word, inicio)

    return segmentos_encontrados

def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://hscomercial.mx/'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    container=soup.find(class_="product-page-container")
    if container:
        # SKU
        sku=container.find('span',class_="sku")
        if sku:
            sku_text=sku.text
            product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product_title entry-title")
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text.strip()
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        # time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="price")
        if precio:
            product_information['Precio']=precio.text.strip()
        # time.sleep(1)

        # DESCRIPCION LARGA
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
        
        size=product_information['DescripcionCorta'].split()
        product_information['Tamaño']=size[-1]
 
        # IMAGEN
        imagen_container=container.find(class_="product-images-container")
        imagen=imagen_container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link=imagen.get('src')
                if imagen_link.startswith(URL):
                    product_information['Img']=imagen_link
                else:
                    product_information['Img']=URL+imagen_link
        # time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = ''
    
    driver.get(link)
    # time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find('nav',class_="woocommerce-pagination")

    if main_body:
        pagination_html=main_body.find('ul',class_="page-numbers").find_all('li')
            
        if pagination_html:
            pages_urls=pagination_html[-2].find('a')
            last_page=pages_urls.get('href').split('/')[-2]
            for i in range(1,int(last_page)+1):
                page_link=link+f'/page/{i}/'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_dulces(driver, fecha):
    INFORMANTE = 'H. S. Comercial'
    URL = 'https://hscomercial.mx/dulces-mayorista-marcas-de-dulces/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="main")
    categories=menu.find_all('div', class_=lambda value: value and value.endswith('column'))
    
    counter=0
    for category in categories:
        #
        # categoria_container=category.find(class_="has-text-align-center has-woostify-heading-6-font-size")
        categoria_container=category.find(lambda tag:tag.name != 'div')
        categoria=categoria_container.text
        link_categoria=category.find('figcaption').find('a').get('href')
        print(categoria)
        print(link_categoria)
        
        driver.get(link_categoria)
        html_source=driver.page_source
        soup=BeautifulSoup(html_source,'html.parser')
        
        main_container=soup.find(id="main")
        main_list=main_container.find('ul',class_="products columns-4 tablet-columns-4 mobile-columns-2")
        products=main_list.find_all('li')

        for product in products:
            link=product.find('a')
            driver.get(link.get('href'))
            dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria,fecha)
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

    os.environ["WDM_LOCAL"] = '1'
    os.environ["WDM_PATH"] = driver_path

    driver_manager = ChromeDriverManager().install()
    

    driver = webdriver.Chrome(service=Service(driver_manager), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_dulces(driver,stamped_today)
    filename='hscomercial_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    # link='https://lamediterranea.mx/categoria-producto/licores-y-destilados'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

