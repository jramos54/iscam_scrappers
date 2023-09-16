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


def agregar_informacion(soup,informante,fecha):
    product_information = {
        'Informante': informante,
        'Categoria': '',
        'DescripcionCorta': '',
        'DescripcionLarga': '',
        'SKU': '',
        'Etiqueta': '',
        'Img': '',
        'Precio': '',
        'Fecha': fecha
        }
    cat_container=soup.find('nav',class_="woocommerce-breadcrumb")
    if cat_container:
        links=cat_container.find_all('a')
        categoria=links[-1].text.strip()
        # etiqueta=links[-1].text.strip()
        product_information['Categoria']=categoria
        # product_information['Etiqueta']=etiqueta

    container=soup.find('div', {'data-elementor-type': 'product'})
    if container:
        descripcion_corta=container.find('h1')
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text

        descripcion_larga=container.find(id="tab-description")
        if descripcion_larga:
            txt_desc=descripcion_larga.text
            descripcion_larga_=txt_desc.splitlines()
            product_information['DescripcionLarga']='. '.join(elemento for elemento in descripcion_larga_ if elemento.strip() != '')

        sku=container.find('span',class_="sku")
        if sku:
            product_information['SKU']=sku.text.strip()

        imagen=container.find('img', {'role': 'presentation'})
        if imagen:
            product_information['Img']=imagen.get('src')

        precio=container.find('span',class_="woocommerce-Price-amount amount")
        if precio:
            product_information['Precio']=precio.text

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

    return product_information


def pagination(driver,link):
   
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    next_page_item=soup.find('a',class_="next page-numbers")
    pagination_html=next_page_item.parent.previous_sibling 

    pages.append(link)

    if pagination_html:
        total_pages_link=pagination_html.find('a').text
    
        total_pages=int(total_pages_link)
        for i in range(2,total_pages+1):
            pages.append(link+'page/'+f'{i}'+'/')

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Ofimart'
    URL = 'https://ofimart.mx/tienda/'
    informacion = []

    pages=pagination(driver,URL)
    counter=0

    for page in pages:
        driver.get(page)
        page_html=BeautifulSoup(driver.page_source,'html.parser')
        products_content=page_html.find('ul',class_="products elementor-grid columns-4")
        if products_content:
            products=products_content.find_all('li')

            for product in products:
                time.sleep(2)
                product_link=product.find('a')
                # print(product_link.get('href'))
                driver.get(product_link.get('href'))
                
                producto=agregar_informacion(
                    BeautifulSoup(driver.page_source, 'html.parser'),
                    INFORMANTE,fecha)
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

    driver_manager = ChromeDriverManager(path=driver_path,version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_papelera(driver,stamped_today)
    filename='Ofimart_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)

    # link='https://ofimart.mx/tienda/'
    # for k,i in enumerate(pagination(driver,link)):
    #     print(f"{k}--{i}")
    #     session = requests.Session()
    #     response=requests.get(i)
    #     print(response.status_code)
    
    
    driver.quit()

    print(f"{time.time()-inicio}")

