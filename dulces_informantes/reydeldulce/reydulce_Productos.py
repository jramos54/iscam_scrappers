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
    URL = 'https://www.elreydeldulce.com/en/shop'
    URL_BASE='https://www.elreydeldulce.com'
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
    container=soup.find(id="product_detail")
    if container:
        # SKU
        # sku=container.find('span',class_="sku")
        # if sku:
        #     sku_text=sku.text
        #     product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(itemprop="name")
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text.strip()
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        # time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="oe_price")
        if precio:
            product_information['Precio']=precio.text.strip()
        # time.sleep(1)

        # DESCRIPCION LARGA
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
        
        size=product_information['DescripcionCorta'].split()
        if len(size)>3:
            if size[-1]=='(copia)':
                product_information['Tamaño']=size[-3]+' '+size[-2]
            else:
                product_information['Tamaño']=size[-2]+' '+size[-1]
 
        # IMAGEN
        imagen_container=container.find(class_="carousel slide")
        imagen=imagen_container.find('img',itemprop="image")
        if imagen:
            if imagen.get('src') != '':
                imagen_link=imagen.get('src')
                if imagen_link.startswith(URL_BASE):
                    product_information['Img']=imagen_link
                else:
                    product_information['Img']=URL_BASE+imagen_link
        # time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = 'https://www.elreydeldulce.com'
    
    driver.get(link)
    time.sleep(2)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="pagination m-0 mt-2 ml-md-2")
    if main_body:
        pagination_html=main_body.find_all('li')
        
        while 'disabled' not in pagination_html[-1].get('class'):

            main_body=soup.find(class_="pagination m-0 mt-2 ml-md-2")
            pagination_html=main_body.find_all('li')
            last_pagination=pagination_html[-2].find('a')
            
            last_url=URL+last_pagination.get('href')
            print(last_url)
            driver.get(last_url)
            html=driver.page_source
            soup=BeautifulSoup(html,'html.parser')

        
        last_page=last_url.split('/')[-1]
        for i in range(1,int(last_page)+1):
            page_link=link+f'/page/{i}'
            pages.append(page_link)
        
    else:
        pages.append(link)

    return tuple(pages)


def productos_dulces(driver, fecha):
    INFORMANTE = 'El rey del Dulce'
    URL = 'https://www.elreydeldulce.com/en/shop'
    URL_BASE='https://www.elreydeldulce.com'
    informacion = []
    time.sleep(2)
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="wrap")
    categories=menu.find('ul',id="o_shop_collapse_category").find_all('li',recursive=False)

    counter=0
    categories.pop(0)
    for category in categories:
                
        
        categoria=category.text.strip()
        link_categoria=URL_BASE+category.find('a').get('href')
        print(categoria)
        print(link_categoria)
        time.sleep(2)

        pages=pagination(driver,link_categoria)

        for page in pages:
            print('scrapping  ',page)
            time.sleep(2)
            driver.get(page)
            html_source=driver.page_source
            soup=BeautifulSoup(html_source,'html.parser')
            
            main_container=soup.find(id="products_grid")
            main_list=main_container.find('table')
            products=main_list.find_all('td')

            for product in products:
                link_container=product.find('a',itemprop="name")
                link=URL_BASE+link_container.get('href')
                time.sleep(2)
                driver.get(link)
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
    filename='reydulce_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    # link='https://www.elreydeldulce.com/en/shop/category/chocolates-10'
    # pages=pagination(driver,link)
    
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

