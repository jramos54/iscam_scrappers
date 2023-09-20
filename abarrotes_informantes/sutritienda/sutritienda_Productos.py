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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup
def tamano_producto(cadena):
    match = re.search(r'\d+\s*[A-Za-z]+', cadena)
    
    if match:
        return match.group()
    else:
        return ''

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

def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto

def agregar_informacion(soup,informante,fecha):
    URL = ''
    product_information = {
        'Informante': informante,
        'Categoria':'',
        'SKU':'',
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Marca':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    
    categoria_section=soup.find(class_="bread-crumbs")
    if categoria_section:
        categoria=categoria_section.find_all('li')
        categoria_item=categoria[-1]
        product_information['Categoria']=categoria_item.text.strip()
    
    container=soup.find(class_="product-detail")
    if container:
        # SKU
        sku=container.find('div',class_="skuReference")
        if sku:
            sku_text=sku.text
            product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product-detail__name")
        if descripcion_corta:
            caracteres_eliminar = ['-', '"', '.']
            descripcion_text=descripcion_corta.text.strip()

            product_information['DescripcionCorta']=descripcion_text
            #  # MARCA
            marca_text=product_information['DescripcionCorta'].split('-')
            if len(marca_text)>=3:
                product_information['Marca']=marca_text[-2].strip()

            # Tamano
            size=product_information['DescripcionCorta'].split('-')
            product_information['Tamaño']=tamano_producto(size[0])

        # time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="productPrice")
        if precio:
            precio_text=precio.text.strip()
            symbol_loc=precio_text.find('$')
            product_information['Precio']=precio_text[symbol_loc:]
        # time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="productDescription").find('p')
        
        if descripcion_larga:
            lines=descripcion_larga.text.splitlines()
            product_information['DescripcionLarga']=' '.join(lines).strip()
 
        # IMAGEN
        imagen_container=container.find(class_="images product-detail__image")
        if imagen_container:
            imagen=imagen_container.find('img')
            if imagen:
                
                imagen_link=imagen.get('src')
                
                product_information['Img']=imagen_link
                
        time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = ''
    
    driver.get(link)
    time.sleep(2)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="pages")

    if main_body:
        
        pages_urls=main_body.find_all('a')
        last_page=pages_urls[-1].get('href').split('/')[-2]
        for i in range(1,int(last_page)+1):
            page_link=link+f'page/{i}/'
            pages.append(page_link)
    else:
        pages.append(link)
    

    return pages


def productos_abarrotes(driver, fecha):
    INFORMANTE = 'Sutritienda'
    URL = 'https://www.surtitienda.mx'
    BASE_URL=''
    informacion = []

    driver.get(URL)
    # time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(class_="site-nav").find('ul')

    sub_menus=menu.find_all('li',recursive=False)
    category_links=[]
    for sub_menu in sub_menus:
        menu_category=sub_menu.find('ul')
        sub_menu_categories=menu_category.find_all('li',recursive=False)
        for sub_menu_category in sub_menu_categories:
            # categoria=sub_menu_category.find('a').text
            # print(categoria)
            category_link=sub_menu_category.find('ul')
            if category_link:
                sub_categorias_links=category_link.find_all('a')
                for sub_categoria_link in sub_categorias_links:
                    category_url=URL+sub_categoria_link.get('href')
                    category_links.append(category_url)

    
    counter=0

    for category_link in category_links:
        # time.sleep(5)
        print(category_link)
        driver.get(category_link)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        product_container=soup.find(class_="prateleira vitrine")
        if product_container:
            products=product_container.find_all('div',class_="product-item")

            time.sleep(2)
    #     pages=pagination(driver,link_categoria)
        
    #     for page in pages:
    #         print(page)

    #         driver.get(page)
    #         time.sleep(2)
    #         html_source=driver.page_source
    #         soup=BeautifulSoup(html_source,'html.parser')
        
    #         main_container=soup.find(class_="products grid")

    #         products=main_container.find_all('li',recursive=False)

            for product in products:
                link_product=product.find('a',class_="dl-product-link")
                link=link_product.get('href')
                print(link)
                driver.get(link)
                time.sleep(5)
                dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,fecha)
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

    datos=productos_abarrotes(driver,stamped_today)
    filename='sutritienda_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    # link='https://farmadepot.com.mx/categoria-producto/perfumeria/'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

