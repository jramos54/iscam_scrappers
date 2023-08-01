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
    container=soup.find('div',class_="page-wrap").find('div',class_="page-area")
    if container:
        descripcion_corta=container.find('div',class_="summary entry-summary").find('h1')
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text

        # descripcion_larga=container.find('table',class_="woocommerce-product-attributes shop_attributes").text
        # descripcion_larga_=descripcion_larga.splitlines()
        # if descripcion_larga:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']

        # sku=container.find('span',class_="sku")
        # if sku:
        #     product_information['SKU']=sku.text

        imagen_element=container.find('figure',class_="woocommerce-product-gallery__wrapper")
        imagen=imagen_element.find('img')
        if imagen:
            product_information['Img']=imagen.get('src')

        precio=container.find('div',class_="summary entry-summary").find('p',class_="price")
        if precio:
            product_information['Precio']=precio.text.strip()
        
        etiqueta=container.find('span',class_="posted_in")
        if etiqueta:
            product_information['Etiqueta']=etiqueta.find('a').text

        # json_prod=json.dumps(product_information,indent=4)
        # print(json_prod)

    return product_information


def pagination(driver,link):
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('ul',class_="page-numbers")

    pages.append(link)

    if pagination_html:
        paginas=pagination_html.find_all('li')
        last_page_link=paginas[-1].find('a').get('href')
        
        last_page=int(last_page_link.strip().split('/')[-2])
        
        for i in range(2,last_page+1):
            pages.append(link+'/page/'+f'{i}'+'/')

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papeleria la Palma'
    URL = 'https://papelerialapalma.com/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find('div',class_="page-wrap")
    
    lista_level0=menu.find(id="text-5")
    itemslevel0=lista_level0.find_all('a',recursive=True)

    counter=0
    for itemlevel0 in itemslevel0:
        categoria=itemlevel0.text
        # print(itemlevel0.find('span').text)
        # print('-'*40)
        link=itemlevel0.get('href')
        print(categoria)
        if categoria=='Nuevos':
            continue
        pages=pagination(driver,link)
        
        for page in pages:
            driver.get(page)
            page_html=BeautifulSoup(driver.page_source,'html.parser')

            products_content=page_html.find('ul',class_="products columns-4")
            if products_content:
                products=products_content.find_all('li')

                for product in products:
                    
                    product_link=product.find('a',class_='woocommerce-LoopProduct-link woocommerce-loop-product__link')
                    
                    # print(product_link.get('href'))
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
    chrome_options.add_argument("--ignore-certificate-errors")

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    driver_manager = ChromeDriverManager(path=driver_path)
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_papelera(driver,stamped_today)
    filename='Papelerialapalma_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)

    # link='https://superpapelera.com.mx/escolar/utiles-escolares/cuadernos-blocks-y-libretas/'
    # for i in pagination(driver,link):
    #     response=requests.get(i)
    #     print(response.status_code)
    
    driver.quit()

    print(f"{time.time()-inicio}")

