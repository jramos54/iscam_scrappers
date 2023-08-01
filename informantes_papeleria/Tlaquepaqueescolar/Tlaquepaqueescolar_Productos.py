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
    URL='https://www.tlaquepaqueescolar.com.mx/Te2023/'
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
    
    descripcion_corta=soup.find('h3')
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text.strip()
        product_information['DescripcionLarga']=descripcion_corta.text.strip()

    # descripcion_larga=soup.find('p',class_="text-justify")
    # if descripcion_larga:
    #     product_information['DescripcionLarga']=descripcion_larga.text

    sku=soup.find_all('div')
    if sku:
        product_information['SKU']=sku[-1].text[9:]

    imagen=soup.find('img')
    if imagen:
        product_information['Img']=URL+imagen.get('src')

    # precio=soup.find('h2',class_='text-primary')
    # if precio:
    #     product_information['Precio']=precio.text.strip()

    # json_prod=json.dumps(product_information,indent=4)
    # print(json_prod)
    if product_information['SKU'] =="" and product_information['DescripcionCorta']=='':
        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)
        return None

    return product_information

def extract_products(container):
    container_1 = container.find('div')
    container_2 = container_1.find_all('div', recursive=False)
    products = container_2[-1].find_all('div', recursive=False)
    return products

def process_category(driver, category_url, informacion, INFORMANTE, categoria, fecha,URL):
    driver.get(category_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    container = soup.find(id="section-5")
    products = extract_products(container)

    for product in products:
        subcat = product.find('a')
        if subcat:
            link_target = subcat.get('href')
            link = URL + link_target
            process_category(driver, link, informacion, INFORMANTE, categoria,fecha,URL)
        else:
            producto = agregar_informacion(
                product,
                INFORMANTE, categoria, fecha)
            if producto:
                informacion.append(producto)
            # counter += 1
            # print(counter)




def productos_papelera(driver, fecha):
    INFORMANTE = 'Tlaquepaque Escolar'
    URL_escolar = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogoescolar.html'
    URL_oficina = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogooficinas.html'
    URL='https://www.tlaquepaqueescolar.com.mx/Te2023/'
    informacion = []
    urls=[URL_escolar,URL_oficina]
    counter=0
    for url in urls:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        menu = soup.find(id="section-5")
        itemslevel0=menu.find_all('a',recursive=True)

#######################################################################
        for itemlevel0 in itemslevel0:
            categoria = itemlevel0.text
            print(categoria)
            link_target = itemlevel0.get('href')
            link = URL + link_target
            process_category(driver, link, informacion, INFORMANTE,categoria, fecha,URL)        
        # for itemlevel0 in itemslevel0:
        #     categoria=itemlevel0.text
        #     print(categoria)
        #     link_target=itemlevel0.get('href')
        #     link=URL+link_target
        #     driver.get(link)
            
        #     soup=BeautifulSoup(driver.page_source, 'html.parser')
        #     container=soup.find(id="section-5")
        #     # print(container)

        #     container_1=container.find('div')
        #     # products=container.find_all('div',class_="col-md-4 section-5-box wow fadeInUp")
        #     container_2=container_1.find_all('div',recursive=False)

        #     # print(container_2[-1])
        #     products=container_2[-1].find_all('div',recursive=False)
            
        #     for product in products:

        #         subcat=product.find('a')
        #         if subcat:
        #             link_target=subcat.get('href')
        #             link=URL+link_target

        #             driver.get(link)
        #             soup=BeautifulSoup(driver.page_source, 'html.parser')
        #             container=soup.find(id="section-5")
        #             container_1=container.find('div')
        #             container_2=container_1.find_all('div',recursive=False)
        #             productos=container_2[-1].find_all('div',recursive=False)
        #             for item in productos:
        #                 producto=agregar_informacion(
        #                     item,
        #                     INFORMANTE,categoria,fecha)
        #                 informacion.append(producto)
        #                 counter+=1
        #                 print(counter)
        #         else:
        #             producto=agregar_informacion(
        #                 product,
        #                 INFORMANTE,categoria,fecha)
        #             informacion.append(producto)
        #             counter+=1
        #             print(counter)

    return informacion            
                

if __name__=='__main__':
    URL_escolar = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogoescolar.html'
    URL_oficina = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogooficinas.html'
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

    driver_manager = ChromeDriverManager()
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    response=requests.get(URL_escolar)
    
    if response.status_code==200:
        datos=productos_papelera(driver,stamped_today)
        filename='Tlaquepaque_productos_'+stamped_today+'.csv'
        funciones.exportar_csv(datos,filename)
    else:
        print('sin conexion')
    driver.quit()

    print(f"{time.time()-inicio}")

