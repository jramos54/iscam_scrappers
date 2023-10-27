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

def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://www.dulceriasalazar.com/pages/categorias'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
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
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product-meta__title")
        if descripcion_corta:
            caracteres_eliminar = ['-', '"', '.']
            descripcion_text=descripcion_corta.text.strip()

            product_information['DescripcionCorta']=limpiar_texto(descripcion_text,caracteres_eliminar)
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        # time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="price")
        if precio:
            precio_text=precio.text.strip()
            symbol_loc=precio_text.find('$')
            product_information['Precio']=precio_text[symbol_loc:]
        # time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="rte text--pull")
        
        if descripcion_larga:
            lines=descripcion_larga.text.splitlines()
            product_information['DescripcionLarga']=' '.join(lines).strip()
 
        # IMAGEN
        imagen_container=container.find(class_="product-gallery product-gallery--with-thumbnails")
        if imagen_container:
            imagen=imagen_container.find('img',class_="product-gallery__image image--fade-in lazyautosizes lazyloaded")
            if imagen:
                if imagen.get('data-zoom') != '':
                    imagen_link=imagen.get('data-zoom')
                    
                    product_information['Img']='https:'+imagen_link
                
        # time.sleep(1)

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


def productos_abarrotes(driver, fecha):
    INFORMANTE = 'Distribuidora almacenes de la Frontera (SUPERETTE)'
    URL = 'https://superette-app.web.app/tabs/tab2'
    BASE_URL=''
    informacion = []

    driver.get(URL)
    # time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(class_="ion-page")

    content_page=menu.find(class_="hydrated")
    
    shadow_hydrated=driver.execute_script("return document.querySelector('ion-router-outlet').shadowRoot.querySelector('slot')")
   
   
    shadow=driver.execute_script("return document.querySelector('ion-content').shadowRoot.querySelector('main')")
    
    assigned_nodes = driver.execute_script('return arguments[0].querySelector("slot").assignedNodes()', shadow)
    app_home = next(node for node in assigned_nodes if node.tag_name == "app-home")
    
    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'col-6 col-sm-6 col-md-4 col-lg-3 p-2 d-flex flex-column'))
    WebDriverWait(driver, 10).until(element_present)
   

    # containers=shadow.find_all('div', class_="col-6 col-sm-6 col-md-4 col-lg-3 p-2 d-flex flex-column")

    # categories=[]
    # for container in containers:
    #     print(container)
    #     elemento = driver.find_element(By.CLASS_NAME, "w-100")
    #     elemento.click()
    #     link=driver.current_url
    #     print(link)


    # counter=0
    # for category in categories:
       
    #     categoria=category.text.strip()
    #     link_categoria=BASE_URL+category.get('href')
    #     print(categoria)
    #     print(link_categoria)
    #     time.sleep(2)
    #     pages=pagination(driver,link_categoria)
        
    #     for page in pages:
    #         print(page)

    #         driver.get(page)
    #         time.sleep(2)
    #         html_source=driver.page_source
    #         soup=BeautifulSoup(html_source,'html.parser')
        
    #         main_container=soup.find(id="main")

    #         main_list=main_container.find(class_="product-list product-list--collection product-list--with-sidebar")
    #         if main_list:
    #             products=main_list.find_all('div',recursive=False)

    #             for product in products:
    #                 link_product=product.find('a',class_="product-item__title text--strong link")
    #                 link=BASE_URL+link_product.get('href')
    #                 print(link)
    #                 driver.get(link)
    #                 time.sleep(2)
    #                 dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria,fecha)
    #                 informacion.append(dato)
    #                 counter+=1
    #                 print(counter)
            
    # return informacion           
                

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
    filename='superette_productos_'+stamped_today+'.csv'
    # funciones.exportar_csv(datos,filename)
    
    # link='https://lamediterranea.mx/categoria-producto/licores-y-destilados'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

