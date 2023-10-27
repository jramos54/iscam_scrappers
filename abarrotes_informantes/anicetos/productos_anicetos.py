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
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

import funciones
from bs4 import BeautifulSoup

def login_page(driver):
    URL='https://dunosusapromociones.com/pickup/sesion'
    username='jrmsmolina54@gmail.com'
    password='arioto02'
        
    driver.get(URL)
    print('haciendo login')
    driver.find_element(By.ID,'usuario_login').send_keys(username)
    driver.find_element(By.ID,'password_login').send_keys(password)
    driver.find_element(By.ID,'begin').click()
    time.sleep(1)
    print('Seleccionando Tienda')
    ciudad_button = driver.find_element(By.ID,'ciudad_2378')
    ciudad_button.click()
    time.sleep(1)
    tienda_button=driver.find_element(By.ID,'tienda_13')
    tienda_button.click()
    time.sleep(1)
    
  
def sucursal_page(driver):
    URL_base='https://dunosusapromociones.com/pickup/'
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    page_categories=soup.find_all(id='addrow')
    categories=[]
    print('Extrayendo links de categorias')
    for page in page_categories:
        categories_links=page.find_all('a')
        for link_category in categories_links:
            link=URL_base+link_category.get('href')
            # print(link)
            categories.append(link)  
    time.sleep(5)
    return categories  


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
    URL = 'https://losanicetos.mx/productos/'
    product_information = {
        'Informante': informante,
        'SKU':'',
        'Categoria':categoria,
        'DescripcionCorta':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Marca':'',
        'Img':'',
        'Fecha':fecha
        }
    
    texto_item=soup.text.strip()
    lines_texto=texto_item.splitlines()
    filtered_list = [item for item in lines_texto if item.strip()]

    # DESCRIPCION CORTA
    product_information['DescripcionLarga']=' '.join(filtered_list[:-1]).strip()
    product_information['DescripcionCorta']=' '.join(filtered_list[:2]).strip()
    # MARCA
    
    product_information['Marca']=filtered_list[0].strip()
  
    # SKU
    sku_text=filtered_list[2]
    sku_loc=sku_text.find(':')
    product_information['SKU']=sku_text[sku_loc+1:].strip()
    # time.sleep(1)

    size_text=filtered_list[1]
    size_partition=size_text.split('/')
    product_information['Tamaño'] = size_partition[-1].strip()
    
    # IMAGEN

    imagen=soup.find('img',class_="jet-carousel__item-img")
    if imagen:
        if imagen.get('src') != '':
            imagen_link=imagen.get('src')
            
            product_information['Img']=imagen_link
            
    # time.sleep(1)
    
    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://dunosusapromociones.com/pickup/'
    print('iniciando paginacion')
    driver.get(link)
    time.sleep(2)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="shop-inner")
    print('Se accesa al link')
    if main_body:
        
        pagination_html=main_body.find(class_="pagination-area")
        list_url=pagination_html.find('ul')  
        print(bool(list_url))
        if list_url:
            print(bool(main_body))
            pages_urls=pagination_html.find_all('a')
            for page in pages_urls:
                link_page=URL+page.get('href')
                # print(link_page)
                pages.append(link_page)
        else:
            pages.append(link)
    else:
        pages.append(link)
    print(link)
    print(pages)
    time.sleep(3)
    return pages

def element_exists(by, value):
    try:
        driver.find_element(by, value)
        return True
    except NoSuchElementException:
        return False

def productos_abarrotes(driver, fecha):
    INFORMANTE = 'Los Anicetos'
    URL = ''
    BASE_URL='https://losanicetos.mx/productos/'
    informacion = []
    counter=0
    
    driver.get(BASE_URL)
    select_category = driver.find_element(By.CSS_SELECTOR,'select.jet-select__control[name="categoria"]')
    categories_selector=Select(select_category)
    
    for option in categories_selector.options:
        category=option.text.strip()
        if category == 'Seleccionar':
            continue
        print(category)
        categories_selector.select_by_value(option.get_attribute("value"))
        time.sleep(10)
        if element_exists(By.CLASS_NAME, 'jet-filters-pagination'):
            print('pagination starts')
            while True:
                # pagination_element = driver.find_element(By.CLASS_NAME, 'jet-filters-pagination')
                time.sleep(5)
                html=driver.page_source
                soup=BeautifulSoup(html,'html.parser')
                product_items = soup.find_all(class_="elementor elementor-248")
                for product in product_items:
                    dato=agregar_informacion(product,INFORMANTE,category,fecha)
                    informacion.append(dato)
                    counter+=1
                    print(counter)
                current_page=soup.find(class_="jet-filters-pagination__item jet-filters-pagination__current")
                print(f"on page {current_page.text}")
                if element_exists(By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']"):
                    element=driver.find_element(By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']")
                    x_offset=element.location['x']
                    y_offset=element.location['y']
                    print(element.location)
                    
                    wait = WebDriverWait(driver, 10)
                    element = driver.find_element(By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']")
                    driver.execute_script("arguments[0].click();", element)
                    
                    # next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']")))

                    # next_button.click()
                    # actions = ActionChains(driver)
                    # actions.move_to_element(element).move_by_offset(x_offset, y_offset).click().perform()

                    driver.implicitly_wait(30)
                else:
                    break
        else:
            print('pagination doesnt exist')
            time.sleep(5)
            html=driver.page_source
            soup=BeautifulSoup(html,'html.parser')
            product_items = soup.find_all(class_="elementor elementor-248")
            
            for product in product_items:
                dato=agregar_informacion(product,INFORMANTE,category,fecha)
                informacion.append(dato)
                counter+=1
                print(counter)
            
        print('='*50)
    # for category_page in categories_pages:
    #     time.sleep(1)
    #     pages=pagination(driver,category_page)
    #     print(category_page)
    #     html = driver.page_source
    #     soup = BeautifulSoup(html, 'html.parser')
    #     categoria=soup.find(class_="f-fam2").text.strip()
    #     print(categoria)

    #     for page in pages:
    #         time.sleep(2)
    #         driver.get(page)
            
    #         print(page)
    #         html = driver.page_source
    #         soup = BeautifulSoup(html, 'html.parser')

    #         menu = soup.find(class_="shop-inner")
            
    #         if menu:
    #             products_area=menu.find(class_="products-grid")
    #             if products_area:
    #                 products=products_area.find_all('li')
    #                 for product in products:
                    
    #                     dato=agregar_informacion(product,INFORMANTE,categoria,fecha)
    #                     informacion.append(dato)
    #                     counter+=1
    #                     print(counter)
            
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
    # login_page(driver)
    # categories_pages=sucursal_page(driver)
    datos=productos_abarrotes(driver,stamped_today)
    filename='anicetos_productos_'+stamped_today+'.csv'
    funciones.exportar_csv(datos,filename)
    
    # link='https://lamediterranea.mx/categoria-producto/licores-y-destilados'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

# logout_link = driver.find_element(By.XPATH,'//div[@class="log out"]/a')
#     logout_link.click()