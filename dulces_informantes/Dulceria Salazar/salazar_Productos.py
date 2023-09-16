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

def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto

def tamano_producto(cadena):
    match = re.search(r'\d+\s*[A-Za-z]+', cadena)
    
    if match:
        return match.group()
    else:
        return ''

def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://www.dulceriasalazar.com/pages/categorias'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'TamañoMayoreo':'',
        'Img':'',
        'Fecha':fecha
        }
    container=soup.find(id="main")
    if container:
        # SKU
        # sku=container.find('span',class_="sku")
        # if sku:
        #     sku_text=sku.text
        #     product_information['SKU']=sku_text.strip()
        time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product-meta__title")
        if descripcion_corta:
            caracteres_eliminar = ['-', '"', '.']
            descripcion_text=descripcion_corta.text.strip()

            product_information['DescripcionCorta']=limpiar_texto(descripcion_text,caracteres_eliminar)
            
            desc_corta_list=product_information['DescripcionCorta'].split()
            if len(desc_corta_list)>1:
                if len(desc_corta_list[-2])>3:
                    size=tamano_producto(desc_corta_list[-2])
                    product_information['Tamaño']=size.strip('\n')
                else:
                    size=tamano_producto(''.join(desc_corta_list[-3:-1]))
                    product_information['Tamaño']=size.strip('\n')

            
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        time.sleep(2)
        
        # PRECIO
        precio=container.find(class_="price")
        if precio:
            precio_text=precio.text.strip()
            symbol_loc=precio_text.find('$')
            product_information['Precio']=precio_text[symbol_loc:]
        time.sleep(2)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="rte text--pull")
        
        if descripcion_larga:
            lines=descripcion_larga.text.splitlines()
            for line in lines:
                if 'caja' in line:
                    caja_loc=line.find('caja')
                    size=tamano_producto(line[caja_loc:])
                    product_information['TamañoMayoreo']=size.strip()
            product_information['DescripcionLarga']=' '.join(lines).strip()
 
        # IMAGEN
        imagen_container=container.find(class_="product-gallery product-gallery--with-thumbnails")
        if imagen_container:
            imagen=imagen_container.find('img',class_="product-gallery__image image--fade-in lazyautosizes lazyloaded")
            if imagen:
                if imagen.get('data-zoom') != '':
                    imagen_link=imagen.get('data-zoom')
                    
                    product_information['Img']='https:'+imagen_link
                
        time.sleep(2)

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

    main_body=soup.find(id="main")

    if main_body:
        pagination_html=main_body.find(class_="pagination__nav")
            
        if pagination_html:
            pages_urls=pagination_html.find_all('a')
            last_page=pages_urls[-1].get('href').split('=')[-1]
            for i in range(1,int(last_page)+1):
                page_link=link+f'?page={i}'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return pages


def productos_dulces(driver, fecha):
    INFORMANTE = 'Dulceria Salazar'
    URL = 'https://www.dulceriasalazar.com/pages/categorias'
    BASE_URL='https://www.dulceriasalazar.com'
    informacion = []

    driver.get(URL)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="main")
    containers=menu.find_all('div', class_="container")
    categories=[]
    for container in containers:
        cat_links=container.find_all('a')
        categories+=cat_links
    
    print(len(categories))
  
    counter=0
    for category in categories:
       
        categoria=category.text.strip()
        link_categoria=BASE_URL+category.get('href')
        print(categoria)
        print(link_categoria)
        time.sleep(2)
        pages=pagination(driver,link_categoria)
        
        for page in pages:
            print(page)

            driver.get(page)
            time.sleep(2)
            html_source=driver.page_source
            soup=BeautifulSoup(html_source,'html.parser')
        
            main_container=soup.find(id="main")

            main_list=main_container.find(class_="product-list product-list--collection product-list--with-sidebar")
            if main_list:
                products=main_list.find_all('div',recursive=False)

                for product in products:
                    link_product=product.find('a',class_="product-item__title text--strong link")
                    link=BASE_URL+link_product.get('href')
                    print(link)
                    driver.get(link)
                    time.sleep(2)
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
    filename='salazar_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    # link='https://lamediterranea.mx/categoria-producto/licores-y-destilados'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

