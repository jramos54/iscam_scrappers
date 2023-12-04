import os
import datetime
import json,re,csv,requests,base64
import time
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
from selenium.common.exceptions import NoSuchElementException


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
        if color == (254, 254, 254) and porcentaje >= valor_1:
            print(f'{color} {porcentaje}')
            negro=True
        elif color == (204, 203, 203) and porcentaje >= valor_2:
            print(f'{color} {porcentaje}')
            gris=True
        elif color == (153, 153, 152) and porcentaje >= valor_3:
            print(f'{color} {porcentaje}')
            light=True
           
    print(f'negro:{negro} gris:{gris} light:{light}')
    if negro and gris:
        return False
    else:
        return True
    

def check_image(link_image):
    imagen_base64=get_image(link_image)
    if verificar_colores_base64(imagen_base64, 82, 9, 4):
        return link_image
                
    else:
        return ''


def scroll(driver, element_xpath, last_height):
    # Aceptar cookies si es necesario
    try:
        button = driver.find_element(By.XPATH, "//button[@data-cookiefirst-action='accept']")
        button.click()
    except NoSuchElementException:
        print('El botón "Ok, continuar" no existe, continúa sin hacer clic')

    time.sleep(2)

    # Calcula la altura necesaria para llegar al footer
    facturacion_xpath = '//*[@id="mod-shop"]/div[2]/footer'
    facturacion = driver.find_element(By.XPATH, facturacion_xpath)
    location_link = facturacion.location
    total_height = max(driver.execute_script("return document.body.scrollHeight"), location_link['y'])

    # Desplazamiento gradual
    for i in range(last_height, total_height, 15):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.25)

    # Desplazamiento directo al footer
    driver.execute_script("arguments[0].scrollIntoView();", facturacion)
    time.sleep(2)

    # Intentar hacer clic en el enlace
    try:
        link = driver.find_element(By.XPATH, element_xpath)
        driver.execute_script("arguments[0].scrollIntoView();", link)
        link.click()
        time.sleep(2)
        print('Saltando a la siguiente pagina')
        return total_height, True
    except Exception as e:
        print('Fin de paginacion')
        return total_height, False


def productos_categorias(category_list,driver):
    informacion=[]
    
    for category in category_list:
        
        link=category[-1]
        print(f"categoria {category[0]} en sub categoria {category[1]}")
        print(link)
        
        # driver.get(link+"?orderById=7&limit=100")
        driver.get(link)
        time.sleep(5)
        
        xpath='/html/body/app-root/app-root/ng-component/div/ng-component/div/div[2]/div/mod-catalog/div/lib-grid/div/div/div[2]/div[2]/cmp-products-grid/div[2]/div[2]/button'
        finish_scroll=True
        last_height = driver.execute_script("return window.innerHeight")
        
        while finish_scroll:
            last_height,finish_scroll=scroll(driver, xpath,last_height)
        
        time.sleep(3)
        html_code=driver.page_source
        soup = BeautifulSoup(html_code,'html.parser')
        container=soup.find(class_="module-shop__content ng-tns-c361-0")
        
        elements=container.find_all("cmp-widget-product")
        totales=container.find(id="grid-totalproducts")
        print(totales.text)
        print(f'productos totales {len(elements)}')

        informacion.append((category[0],category[1],elements))
       
            
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


def producto_informacion(soup_product,informante,categoria,subcategoria,fecha):
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SubCategoria':subcategoria,
        'SKU':'',
        'Marca':'',
        'Presentacion':'',
        'DescripcionCorta':'',
        'Precio':'',
        'Promocion':'',
        'Tamaño':'',
        'DescripcionLarga':'',
        'Img':'',
        'Fecha':fecha
        }
    product_link = {
        'DescripcionCorta':'',
        'LinkProducto':''
    }
    url_base='https://www.merzava.com/es'
    
    # print('='*50)
    # print('producto informacion')
    
    sku=soup_product.find(id="infoproduct-content--code")
    if sku:
        sku_text=sku.text
        product_information['SKU']=sku_text.strip("Código producto:")
    
    presentacion=soup_product.find(id="infoproduct-content--name")
    if presentacion:
        presentacion_text=presentacion.text
        presentacion_segments=presentacion_text.split('-')
        
        product_information['Presentacion']=presentacion_segments[0].strip()
        
        
    descripcion_corta=soup_product.find(id="infoproduct-content--desc")
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text.strip()
        # product_information['DescripcionLarga']=product_information['DescripcionCorta']
        product_information['Tamaño']=tamano_producto(product_information['DescripcionCorta'])
        product_link['DescripcionCorta']=product_information['DescripcionCorta']
    
    precio=soup_product.find(id="infoproduct-content--price")
    if precio:
        product_information['Precio']=precio.text.strip()
        
    promocion=soup_product.find(id="infoproduct-content--offerprice")
    if promocion:
        product_information['Promocion']=promocion.text.strip()
        
    descripcion_larga=soup_product.find(id="info-product--tabs")
    if descripcion_larga:
        descripcion_larga_lines=descripcion_larga.text.splitlines()
        product_information['DescripcionLarga']=''.join(descripcion_larga_lines)
    
    imagen=soup_product.find(class_="image-primary")
    if imagen:
        image=imagen.find('img')
        link_image=image.get('src')
        imagen_link=check_image(link_image)
        product_information['Img']=imagen_link
        
    # link_producto=soup_product.find('a')
    # if link_producto:
    #     product_link['LinkProducto']=url_base+link_producto.get('href')
    
    marca=soup_product.find(id="infoproduct-content--brand")
    if marca:
        product_information['Marca'] = marca.text.strip()

        
    print(json.dumps(product_information,indent=4))
    
    return product_information
          

def productos_informante(url,driver,fecha):
    informante='Grupo Merza'
    informacion=[]
    driver.get(url)
    
    time.sleep(3)
    # driver.save_screenshot("captura_de_pantalla.png")
  
    category_list=[]

    elements=element = driver.find_elements(By.CSS_SELECTOR, "li.nav-item.ng-star-inserted")
    for element in elements:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        # driver.implicitly_wait(5)
        time.sleep(5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        category=element.text
        
        container=soup.find('div',class_="d-flex justify-content-center")
        sub_categories=container.find_all('li')
        
        for sub_category in sub_categories:
            sub_category_element=sub_category.find('a').get('href')
            sub_category_link=url[:-1]+sub_category_element[2:]
            category_list.append((category,sub_category.text,sub_category_link)) 
            
    products=productos_categorias(category_list,driver)
    
    counter=0
    for product in products:
        
        categoria=product[0]
        subcategoria=product[1]
        print(categoria, print(len(products)))
        soup_products=product[-1]
        for soup_product in soup_products:
            
            product_link_container=soup_product.find('a')
            product_link=url[:-3]+product_link_container.get('href')
            print(product_link)
            driver.get(product_link)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
                                  
            product_info=producto_informacion(soup,informante,categoria,subcategoria,fecha)
            informacion.append(product_info)
            counter+=1
            print(counter)
    
    return informacion
    
    
if __name__=='__main__':
    inicio=time.time()
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-urlfetcher-cert-requests")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)
    today = datetime.datetime.now()
    stamped_today = today.strftime("%Y-%m-%d")
    
    URL="https://www.merzava.com/es"
    file_name='productos_grupoMerza_'+stamped_today+'.csv'
    
    # products,links=productos_informante(URL,driver,stamped_today)
    # exportar_csv(products,file_name)
    
    # file_name='links_grupoMerza_'+stamped_today+'.csv'
    # exportar_csv(links,file_name)
    
    
    elements=[('Alimentacion', 'Aceites y grasas comestibles', 'https://www.merzava.com/es/c/alimentos-preparados-y-congelados/102')]
    products = productos_categorias(elements,driver)
    
    for product in products:
        
        categoria=product[0]
        subcategoria=product[1]
        print(categoria, print(len(products)))
        soup_products=product[-1]
        for soup_product in soup_products:
            
            product_link_container=soup_product.find('a')
            product_link=URL[:-3]+product_link_container.get('href')
            print(product_link)
            driver.get(product_link)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')                        
            product_info=producto_informacion(soup,'merza',categoria,subcategoria,'hoy')  
              
              
              
    # url='https://www.tiendaenlinea.7-eleven.com.mx/galletas'
    # driver.get(url)
    # time.sleep(6)
    # html_code=driver.page_source
    # soup = BeautifulSoup(html_code,'html.parser')
    # elements=soup.find_all(class_="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4")
    # print(f'productos totales {len(elements)}')
    # for element in elements:
        
    #     producto_informacion(element,'informante','element[0]',stamped_today)

    driver.quit()