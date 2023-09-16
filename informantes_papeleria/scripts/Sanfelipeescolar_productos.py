"""
Scripts para obtener los productos de los informantes
"""
import os
import datetime
import json
import time

# Importar Selenium webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def productos_sanfelipeescolar(driver, fecha):
    INFORMANTE = 'San Felipe Escolar'
    URL = 'https://online.sanfelipeescolar.com.mx/'
    informacion = []

    contador=0

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="menu-item-23")
    menu_items = menu.select('.ct-menu-link')

    for item in menu_items:
        if item.get('href') != '#':
            categoria = item.get_text()
            link = item.get('href')

            driver.get(link)
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')
            product_list = soup.find('ul', {'data-products': 'type-1'})

            if product_list is not None:
                products = product_list.find_all('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link')

                for product in products:
                    product_information = {
                        'Informante': INFORMANTE,
                        'Categoria': categoria,
                        'DescripcionCorta': '',
                        'DescripcionLarga': '',
                        'SKU': '',
                        'Etiqueta': '',
                        'Img': '',
                        'Precio': '',
                        'Fecha': fecha
                    }
  
                    driver.get(product.get('href'))
                    html_product = driver.page_source
                    soup = BeautifulSoup(html_product, 'html.parser')
                    product_details = soup.find('div', class_='product-entry-wrapper')

                    descripcion_corta = product_details.find('h1', class_='product_title entry-title')
                    if descripcion_corta:
                        product_information['DescripcionCorta'] = descripcion_corta.get_text()

                    descripcion_larga = product_details.find('div', class_='woocommerce-product-details__short-description')
                    if descripcion_larga:
                        descripcion_larga_= descripcion_larga.get_text()
                        product_information['DescripcionLarga'] = ". ".join(descripcion_larga_.splitlines())

                    sku = product_details.find('span', class_='sku')
                    if sku:
                        product_information['SKU'] = sku.get_text()

                    etiqueta = product_details.find('span', class_='tagged_as')
                    if etiqueta:
                        product_information['Etiqueta'] = etiqueta.get_text()

                    precio = product_details.find('p', class_='price')
                    if precio:
                        product_information['Precio'] = precio.get_text()

                    imagen = product_details.find('a', class_='ct-image-container')
                    if imagen:
                        product_information['Img'] = imagen.get('href')
                    
                    contador+=1
                    print(contador)
                    informacion.append(product_information)

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

    datos=productos_sanfelipeescolar(driver,stamped_today)
    filename='sanfelipeescolar_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)