import os,datetime,json,time,requests,re,csv,argparse

import googlemaps

import base64

from PIL import Image
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def get_image(imagen_url):
    respuesta = requests.get(imagen_url)

    if respuesta.status_code == 200:
        imagen_base64 = base64.b64encode(respuesta.content).decode('utf-8')
        
    return imagen_base64


def base64_to_numpy(imagen_base64):
    imagen_bytes = base64.b64decode(imagen_base64)
    imagen = Image.open(BytesIO(imagen_bytes))

    imagen_np = np.array(imagen)

    return imagen_np


def color_percentage(imagen_base64, num_clusters):
    imagen_np = base64_to_numpy(imagen_base64)
    if imagen_np.size % 4 != 0:
        print("La imagen no tiene un tamaño válido para reshape.")
        return {(0, 0, 0): 100.0}  # Valor por defecto
    pixeles = imagen_np.reshape(-1, 4)  # 4 para RGBA

    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixeles)

    labels = kmeans.labels_

    colores = defaultdict(int)

    total_pixeles = len(labels)
    for label in labels:
        color = tuple(map(int, kmeans.cluster_centers_[label][:3]))  
        colores[color] += 1

    colores_porcentaje = {}
    for color, count in colores.items():
        porcentaje = (count / total_pixeles) * 100
        colores_porcentaje[color] = porcentaje

    return colores_porcentaje


def verificar_colores_base64(imagen_base64, valor_1, valor_2, valor_3):
    resultados = color_percentage(imagen_base64, 10)  
    negro=False
    gris=False
    light=False
    for color, porcentaje in resultados.items():
        
        print(f'{color} {porcentaje}')
        if color == (54, 54, 54) and porcentaje >= valor_1:
            print(f'{color} {porcentaje}')
            negro=True
        elif color == (5, 5, 5) and porcentaje >= valor_2:
            print(f'{color} {porcentaje}')
            gris=True
           
    print(f'negro:{negro} gris:{gris} light:{light}')
    if negro and gris:
        return False
    else:
        return True
    

def check_image(link_image):
    imagen_base64=get_image(link_image)
    if verificar_colores_base64(imagen_base64, 90, 3, 3):
        return link_image
                
    else:
        return ''


def scroll(driver, element_xpath,last_height):
    
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    
    for i in range(last_height, total_height, 50):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.25)
    
    # driver.save_screenshot("bottom_page.png")
    last_height = total_height
    try:
        link = driver.find_element(By.XPATH, element_xpath)
        ActionChains(driver).move_to_element(link).click().perform()
        time.sleep(5)
        print('Saltando a la siguiente pagina')
        return last_height,True
    except Exception as e:
        print('Fin de paginacion')
        return last_height,False


def productos_categorias(category_list,driver):
    # print('='*50,'\n','='*50)
    informacion=[]
    for category in category_list:
        print(category)
        link=category[-1]
        print(f"categoria {category[0]} en sub categoria {category[1]}")
        print(link)
        
        marcas=[]
               
        driver.get(link)
        time.sleep(5)
            
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'].vtex-checkbox__input")
        # print('checkboxes',checkboxes)
        for checkbox in checkboxes:
            # print(checkbox.get_attribute('name'))
            marcas.append(checkbox.get_attribute('name'))
        
        xpath='/html/body/div[2]/div/div[1]/div/div[2]/div/div/section/div[2]/div/div[3]/div/div[2]/div/div[4]/div/div/div/div/div/a'
        finish_scroll=True
        last_height = driver.execute_script("return window.innerHeight")
        
        while finish_scroll:
            last_height,finish_scroll=scroll(driver, xpath,last_height)
        
        html_code=driver.page_source
        soup = BeautifulSoup(html_code,'html.parser')
        elements=soup.find_all(class_="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4")
        print(f'productos totales {len(elements)}')

        informacion.append((category[0],category[1],marcas,elements))
       
            
    return informacion


def tamano_producto(cadena):
    match = re.search(r'\d+\s*[A-Za-z]+', cadena)
    
    if match:
        return match.group()
    else:
        return ''


def exportar_csv(diccionarios, nombre_archivo):
    # Obtener las claves del primer diccionario para definir los encabezados del CSV
    encabezados = diccionarios[0].keys()

    with open(nombre_archivo, 'w', newline='',encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados, delimiter='|')

        # Escribir los encabezados en la primera línea del CSV
        writer.writeheader()

        # Escribir cada diccionario como una línea en el CSV
        for diccionario in diccionarios:
            writer.writerow(diccionario)


def producto_informacion(soup_product,informante,categoria,subcategoria,marcas,fecha):
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SubCategoria':subcategoria,
        'Marca':'',
        'DescripcionCorta':'',
        'Precio':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    product_link = {
        'DescripcionCorta':'',
        'LinkProducto':''
    }
    url_base='https://www.tiendaenlinea.7-eleven.com.mx'
    
    print('='*50)
    print('producto informacion')
    
    descripcion_corta=soup_product.find('h3')
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text.strip()
        # product_information['DescripcionLarga']=product_information['DescripcionCorta']
        product_information['Tamaño']=tamano_producto(product_information['DescripcionCorta'])
        product_link['DescripcionCorta']=product_information['DescripcionCorta']
    
    precio=soup_product.find('span',class_="vtex-product-price-1-x-sellingPrice vtex-product-price-1-x-sellingPrice--summary")
    if precio:
        product_information['Precio']=precio.text.strip()
        
    imagen=soup_product.find('img')
    if imagen:
        link_image=imagen.get('src')
        imagen_link=check_image(link_image)
        product_information['Img']=imagen_link
        
    link_producto=soup_product.find('a')
    if link_producto:
        product_link['LinkProducto']=url_base+link_producto.get('href')
    
    for marca in marcas:
        if marca.lower() in product_information['DescripcionCorta'].lower():
            product_information['Marca'] = marca.title()
            break
        
    print(json.dumps(product_information,indent=4))
    print(json.dumps(product_link,indent=4))
    
    return product_information,product_link
          

def productos_informante(url,driver,fecha):
    informante='7-eleven'
    informacion=[]
    product_links=[]
    driver.get(url)
    
    time.sleep(6)
    # driver.save_screenshot("captura_de_pantalla.png")

    menu_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-id='mega-menu-trigger-button']")))
    time.sleep(2)
    menu_button.click()
    time.sleep(3)
    
    print(menu_button.text)
    
    # html = driver.page_source
    # soup = BeautifulSoup(html, 'html.parser')
    # section_1=soup.find(class_="render-container render-route-store-home")
    # section_2=section_1.find(class_="flex flex-column min-vh-100 w-100")

    # categories=section_2.find_all('li',class_="vtex-mega-menu-2-x-menuItem")
    categories=driver.find_elements(By.CSS_SELECTOR,"li.vtex-mega-menu-2-x-menuItem")
    category_list=[]
    sub_category_list=[]
    for category in categories:
        # category_link=category.find('a')
        # category_list.append((category.text,category_link.get('href')))
        
        driver.execute_script("arguments[0].scrollIntoView();", category)
        category_link = category.find_element(By.TAG_NAME, "a").get_attribute("href")
        category_list.append((category.text,category_link))
        ActionChains(driver).move_to_element(category).perform()
        time.sleep(3)
        
        if category.text == '7-Select':
            continue
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        section_1=soup.find(class_="render-container render-route-store-home")
        section_2=section_1.find(class_="flex flex-column min-vh-100 w-100")
        section_3=section_2.find(class_="vtex-mega-menu-2-x-submenuContainer pa5 w-100")
        if section_3:
            
            sub_categories_container = section_3.find_all(class_="vtex-mega-menu-2-x-submenuItem vtex-mega-menu-2-x-submenuItem--isClosed")
            
            for container in sub_categories_container:
            
                sub_categories=container.find_all(class_="vtex-mega-menu-2-x-submenuItem mt3")
                if sub_categories:
                    
                    for sub_category in sub_categories:
                        sub_category_link=sub_category.find('a')
                        sub_category_list.append((category.text,sub_category.text,sub_category_link.get('href')))
                        print((category.text,sub_category.text,sub_category_link.get('href')))
                else:
                    sub_categories=container.find_all(class_="vtex-mega-menu-2-x-styledLinkContainer")
                    for sub_category in sub_categories:
                        sub_category_link=sub_category.find('a')
                        sub_category_list.append((category.text,sub_category.text,sub_category_link.get('href')))
                        print((category.text,sub_category.text,sub_category_link.get('href')))
        else:
            sub_category_list.append((category.text,category.text,category_link))
            print((category.text,category.text,category_link))
            
    products=productos_categorias(sub_category_list,driver)
    
    counter=0
    for product in products:
        
        categoria=product[0]
        subcategoria=product[1]
        marcas=product[2]
        print(categoria)
        soup_products=product[-1]
        for soup_product in soup_products:
            product_info,product_link=producto_informacion(soup_product,informante,categoria,subcategoria,marcas,fecha)
            informacion.append(product_info)
            product_links.append(product_link)
            counter+=1
            print(counter)
    
    return informacion,product_links
    
def main(driver,stamped_today):
    
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()

    # Ejecucion normal del script
    URL="https://www.tiendaenlinea.7-eleven.com.mx/"
    
    products,links=productos_informante(URL,driver,stamped_today)
    filename=args.ruta + 'productos_7-eleven_'+stamped_today+'.csv' 
    exportar_csv(products,filename)
        
        
if __name__=='__main__':
    inicio=time.time()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-urlfetcher-cert-requests")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--js-flags=--max-old-space-size=4096')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--password-store=basic')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # chrome_options.add_argument("--disable-application-cache")
    # chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_argument("--hide-scrollbars")
    # chrome_options.add_argument("--enable-logging")
    # chrome_options.add_argument("--single-process")
    # chrome_options.add_argument("--ignore-certificate-errors")
    # chrome_options.add_argument("--homedir=/tmp")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service":False,
            "profile.password_manager_enabled":False
        }
    )

    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)
    
    today = datetime.datetime.now()
    stamped_today = today.strftime("%Y-%m-%d")
    
    main(driver,stamped_today)

    driver.quit()