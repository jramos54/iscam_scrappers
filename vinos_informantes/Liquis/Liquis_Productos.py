"""
Scripts para obtener los productos de los informantes
"""
import os
import datetime
import json
import time
import requests
import re
import base64

# Importar Selenium webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
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

def agregar_informacion(soup,informante,fecha):
    URL = 'https://liquisonline.com.mx/'
    product_information = {
        'Informante': informante,
        'Categoria':'',
        'SKU':'',
        'DescripcionCorta':'',
        'Tipo':'',
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
    if 'nombre' in soup:
        product_information['DescripcionCorta']=soup['nombre']
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
    else:
        desc=soup['desccorta']
        end_desc=desc.find('$')
        
        product_information['DescripcionCorta']=desc[:end_desc-1].strip()
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
    

    
    if 'codigo' in soup:
        product_information['SKU']=soup['codigo']
    
    if 'precio' in soup:
        product_information['Precio']='$'+soup['precio']
    else:
        precio_find=soup['desccorta'].find('$')
        dot_find=soup['desccorta'].find('.',precio_find)
        precio_text=soup['desccorta'][precio_find:dot_find+2]
    
    patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
    coincidencia = re.search(patron, product_information['DescripcionCorta'].lower())
    if coincidencia:
    # Si se encontró una coincidencia, obtenemos el resultado completo
        resultado = coincidencia.group(1)
        product_information['Tamaño']=resultado

    product_information['Img']=URL+soup['imagen']


    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information
   

def pass_function():
    boton_sucursal = driver.find_element(By.ID, "sucursal_refresh")
    boton_sucursal.click()

    region_selector=Select(driver.find_element(By.ID,"region"))
    region_options=region_selector.options
    
    for region_option in region_options:
        region_option_value=region_option.get_attribute('value')
        region_selector.select_by_value(region_option_value)
        selected_region_option_text = region_selector.first_selected_option.text
        print(f"{region_option_value} - {selected_region_option_text}")

        sucursal_selector=Select(driver.find_element(By.ID,"sucursal"))
        sucursal_options=sucursal_selector.options
        
        for sucursal_option in sucursal_options:
            sucursal_option_value=sucursal_option.get_attribute('value')
            sucursal_selector.select_by_value(sucursal_option_value)
            selected_sucursal_option_text=sucursal_selector.first_selected_option.text
            print(f"{sucursal_option_value} - {selected_sucursal_option_text}")

    boton_entrar=driver.find_element(By.ID,"modal_sucursal_btn")
    boton_entrar.click()

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

def iterations(driver):
    time.sleep(2)
    region_selector=Select(driver.find_element(By.ID,"region"))
    region_options=region_selector.options
    iters=len(region_options)
    # for region_option in region_options:
    #     region_option_value=region_option.get_attribute('value')
    #     region_selector.select_by_value(region_option_value)
        
    #     sucursal_selector=Select(driver.find_element(By.ID,"sucursal"))
    #     sucursal_options=sucursal_selector.options
    #     iters+=len(sucursal_options)

    region_selector.select_by_value('1')
    sucursal_selector=Select(driver.find_element(By.ID,"sucursal"))      
    sucursal_selector.select_by_value('1')
    boton_entrar=driver.find_element(By.ID,"modal_sucursal_btn")
    boton_entrar.click()
    print(f"total iterations {iters}")
    return int(iters)

def scrap_page(driver,informante,fecha):
    informacion=[]
    products_button = driver.find_element(By.CLASS_NAME, 'w3-purple-liquis')
    driver.execute_script("arguments[0].click();", products_button)

    opciones = driver.find_elements(By.CSS_SELECTOR, 'div[data-familia="L"] a')
    for opcion in opciones:
        print('#'*25)
        driver.execute_script("arguments[0].click();", opcion)
        time.sleep(2)
        
        html_code=driver.page_source
        soup = BeautifulSoup(html_code, "html.parser")

        contenedor=soup.find(id="contenedor").find_all()
        
        while contenedor:
            html_code=driver.page_source
            soup = BeautifulSoup(html_code, "html.parser")
            products=soup.find_all('div',class_="w3-card carta")
            for product in products:
                try:
                    base64_object=product.find("div", attrs={"data-v": True})
                    base64_data=base64_object["data-v"]
                    decoded_bytes = base64.b64decode(base64_data)
                    decoded_json = decoded_bytes.decode('utf-8')
                    json_object = json.loads(decoded_json)
                    json_object['desccorta']=product.text.strip()
                    json_object['imagen']=product.find('img').get('src')
                except:
                    json_object={}
                    json_object['desccorta']=product.text.strip()
                    json_object['imagen']=product.find('img').get('src')
                producto=agregar_informacion(json_object,informante,fecha)
                
                if producto:
                    informacion.append(producto)
                    

            next_button=driver.find_element(By.ID, 'navegar_mas')
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)

            contenedor=soup.find(id="contenedor").find_all()
    return informacion
            
def no_repetidos(datos):
    
    unique_set = set()
    unique_data = []

    for diccionario in datos:
        values_tuple = tuple(diccionario.items())
        if values_tuple not in unique_set:
            unique_set.add(values_tuple)
            unique_data.append(diccionario)

    return unique_data


def productos_vinos(driver,fecha):
    INFORMANTE = 'Liquis'
    URL = 'https://liquisonline.com.mx/buscador1.php#'
    driver.get(URL)
    time.sleep(3)

    region_count=1
    sucursal_count=1
    n=iterations(driver)
    counter=1
    resultado=[]
    # pass_function()
    while region_count<n:
        print(counter)
        time.sleep(1)
        boton_sucursal = driver.find_element(By.ID, "sucursal_refresh")
        boton_sucursal.click()

        region_selector=Select(driver.find_element(By.ID,"region"))
        
        region_selector.select_by_value(str(region_count))
        selected_region_option_text = region_selector.first_selected_option.text
        print(selected_region_option_text)
        time.sleep(1)

        sucursal_selector=Select(driver.find_element(By.ID,"sucursal"))
        sucursal_options=sucursal_selector.options
        sucursal_len=len(sucursal_options)
        option_sucursal=sucursal_options[sucursal_count].get_attribute('value')
        
        sucursal_selector.select_by_value(option_sucursal)
        selected_sucursal_option_text=sucursal_selector.first_selected_option.text
        print(selected_sucursal_option_text)
        time.sleep(1)

        sucursal_count+=1

        boton_entrar=driver.find_element(By.ID,"modal_sucursal_btn")
        boton_entrar.click()
        time.sleep(1)
        counter+=1
        print('inicia el scrapping')
        datos=scrap_page(driver,INFORMANTE,fecha)
        for dato in datos:
            resultado.append(dato)

        if sucursal_count>sucursal_len-1:
            region_count+=1
            sucursal_count=1
   
    return resultado            
                

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
    chrome_options.add_argument("--ignore-urlfetcher-cert-requests")

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    os.environ["WDM_LOCAL"] = '1'
    os.environ["WDM_PATH"] = driver_path

    driver_manager = ChromeDriverManager(version="114.0.5735.90")
    driver_manager.install()

    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_vinos(driver,stamped_today)
    filename='liquis_productos_'+stamped_today+'.csv'
    cleaned_data=no_repetidos(datos)
    funciones.exportar_csv(cleaned_data,filename)
    
    # link='https://lamediterranea.mx/categoria-producto/licores-y-destilados'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

