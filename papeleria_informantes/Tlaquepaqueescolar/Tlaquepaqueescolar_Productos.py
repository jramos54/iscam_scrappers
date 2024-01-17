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


def agregar_informacion(soup,informante,categoria,fecha):
    URL='https://tlaquepaqueescolar.com.mx/ecommerce'
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
    
    product_text_container=soup.body.find('div',recursive=False)
    product_text=product_text_container.text.strip()
    product_lines=[line for line in product_text.splitlines() if line !=""]
    print(product_lines)
    

    product_information['DescripcionCorta']=product_lines[0].strip()
    product_information['DescripcionLarga']=' '.join(product_lines[3:-3])

    product_information['SKU']=product_lines[1].strip('SKU: ')

    imagen_container=soup.body.find('div',recursive=False)
    imagen=imagen_container.find('img')
    if imagen:
        imagen_link=imagen.get('src').split('..')
        product_information['Img']=URL+imagen_link[-1]

    
    product_information['Precio']=product_lines[2].strip()
    product_information['Etiqueta']=product_lines[-4].strip()
    
    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)
    # if product_information['SKU'] =="" and product_information['DescripcionCorta']=='':
    #     json_prod=json.dumps(product_information,indent=4)
    #     print(json_prod)
    #     return None

    return product_information

def get_products(driver,link):
    print("==> get productos ")
    try:
        driver.get(link)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        time.sleep(3)
        
        container=soup.find(id='main')#..find('producto')
        fashion_section=container.find(class_="fashion_section")
        # print(fashion_section)
        product_elements=fashion_section.find_all(class_="col-lg-4 col-sm-4")
        links=[]
        
        for product in product_elements:
            product_link=product.find('a')
            link='https://tlaquepaqueescolar.com.mx/ecommerce/modulos/tienda/'+product_link.get('href')
            print(link)
            links.append(link)
        return links
    except:
        return None

def productos_papelera(driver, fecha):
    INFORMANTE = 'Tlaquepaque Escolar'
    
    URL='https://www.tlaquepaqueescolar.com.mx/'
    informacion = []
    counter=0
    
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    menu_container=soup.find(id='navbar')
    menu_dropdown=menu_container.find('li',class_='dropdown').find('ul')
    main_categories=menu_dropdown.find_all('li',recursive=False)
    categories=[]
    for main_category in main_categories:
        elements=main_category.find_all('li')
        categories.extend(elements)
    
    product_items=[]
    for category in categories:
        category_name=category.text.strip()
        category_link=category.find('a').get('href')
        products=get_products(driver,category_link)
        if products:
            product_items.append((category_name,products))
        
    for item in product_items:
        
        categoria=item[0]
        links=item[-1]
        print(categoria)
        for link in links:
            driver.get(link)
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            producto=agregar_informacion(soup,INFORMANTE,categoria,fecha)
            if producto:
                informacion.append(producto)
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
    chrome_options.add_argument('--js-flags=--max-old-space-size=4096')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--password-store=basic')
    
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

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_papelera(driver,stamped_today)
    filename='Tlaquepaque_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    # link="https://tlaquepaqueescolar.com.mx/ecommerce/modulos/tienda/detalles.php?id=TzhJcEdRK0d1b3JqVjllOURPZFhGQT09"
    # driver.get(link)
    # time.sleep(2)
    # html = driver.page_source
    # soup = BeautifulSoup(html, 'html.parser')
    
    # agregar_informacion(soup,"informante","categoria","fecha")
    
    driver.quit()

    print(f"{time.time()-inicio}")

