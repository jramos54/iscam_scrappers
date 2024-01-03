import sys
print(sys.executable)
import os,datetime,json,time,requests,re,csv

import googlemaps

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup



def exportar_csv(diccionarios, nombre_archivo):
    encabezados = diccionarios[0].keys()

    with open(nombre_archivo, 'w', newline='',encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados, delimiter='|')
        writer.writeheader()
        for diccionario in diccionarios:
            writer.writerow(diccionario)


def obtencion_cp(direccion):

    cp_pattern = r'(?:C\.?P\.?|c\.?p\.?)\.?\s+(\d+)'
    match = re.search(cp_pattern, direccion, re.IGNORECASE)
    if match:
        cp = match.group(1)
        return cp
    else:
        gmaps = googlemaps.Client(key='AIzaSyAGm8QGB5w0rp0EiRujJjt_e4wgcwhlKug')
        geocode_result = gmaps.geocode(direccion,components={'country': 'MX'})

        if geocode_result:  
            lista_de_diccionarios=geocode_result[0]['address_components']
            diccionarios_filtrados = [diccionario for diccionario in lista_de_diccionarios if diccionario.get('types') == ['postal_code']]
            if diccionarios_filtrados:
                return diccionarios_filtrados[0]['long_name']
            else:
                return ''
            

def geolocalizacion(direccion):
    gmaps = googlemaps.Client(key='AIzaSyAGm8QGB5w0rp0EiRujJjt_e4wgcwhlKug')

    geocode_result = gmaps.geocode(direccion,components={'country': 'MX'})

    if geocode_result:
        # Extrae la latitud y longitud del resultado
        latitud = geocode_result[0]['geometry']['location']['lat']
        longitud =geocode_result[0]['geometry']['location']['lng']

        return longitud,latitud
    
    else:
        return None,None
    
    
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
    return driver
    
  
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
    URL = 'https://dunosusapromociones.com/pickup/'
    product_information = {
        'Informante': informante,
        'SKU':'',
        'Categoria':categoria,
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    
        

    # DESCRIPCION CORTA
    descripcion_corta=soup.find(class_="item-title")
    if descripcion_corta:
        caracteres_eliminar = ['"', '.']
        descripcion_text=descripcion_corta.text.strip()
        product_information['DescripcionLarga']=limpiar_texto(descripcion_text,caracteres_eliminar)
        
        # MARCA
        # marca_text=product_information['DescripcionCorta'].split()
        # product_information['Marca']=marca_text[0]
        # time.sleep(1)
    
    # SKU
    descripcion_producto=product_information['DescripcionLarga'].split('-')
    # if sku:
    #     sku_text=sku.text
    product_information['SKU']=descripcion_producto[-1].strip()
    # time.sleep(1)

    # time.sleep(1)
    product_information['DescripcionCorta']= descripcion_producto[0].strip()
    # time.sleep(1)

    product_information['Tamaño'] = tamano_producto(product_information['DescripcionCorta'])
    # time.sleep(1)

    # PRECIO
    precio_text=soup.find(class_="regular-price").text
    precio_list=precio_text.split()
    
    product_information['Precio']=''.join(precio_list[:-1])
    # time.sleep(1)

    # DESCRIPCION LARGA
    
    # IMAGEN

    imagen=soup.find('img',class_="first-img")
    if imagen:
        if imagen.get('src') != '':
            imagen_link=imagen.get('src')
            
            product_information['Img']=URL+imagen_link
            
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


def productos_abarrotes(driver, fecha,categories_pages):
    INFORMANTE = 'Dunosusa'
    URL = ''
    BASE_URL='https://dunosusapromociones.com/pickup/'
    informacion = []
    counter=0
    for category_page in categories_pages:
        time.sleep(1)
        pages=pagination(driver,category_page)
        print(category_page)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        categoria=soup.find(class_="f-fam2").text.strip()
        print(categoria)

        for page in pages:
            time.sleep(2)
            driver.get(page)
            
            print(page)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            menu = soup.find(class_="shop-inner")
            
            if menu:
                products_area=menu.find(class_="products-grid")
                if products_area:
                    products=products_area.find_all('li')
                    for product in products:
                    
                        dato=agregar_informacion(product,INFORMANTE,categoria,fecha)
                        informacion.append(dato)
                        counter+=1
                        print(counter)
            
    return informacion           
                

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
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)

    
    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")
    driver=login_page(driver)
    categories_pages=sucursal_page(driver)
    datos=productos_abarrotes(driver,stamped_today,categories_pages)
    filename='dunosusa_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
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