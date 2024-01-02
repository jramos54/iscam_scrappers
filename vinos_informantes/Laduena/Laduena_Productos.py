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
    

def agregar_informacion(soup,informante,categoria,categoria_tipo,fecha):
    URL = 'https:'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Tipo':categoria_tipo,
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
    container=soup.find(id="shopify-section-product-template")

    # sku=container.find('meta',itemprop="sku")
    # if sku:
    #     sku_float=float(sku.get('content'))
    #     sku_str=str(sku_float)
    #     product_information['SKU']=sku_str[:4]

    descripcion_corta=container.find('h1',itemprop="name")
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text
    time.sleep(1)

    # TIPO

    precio=container.find('span',class_="money")
    if precio:
        product_information['Precio']=precio.text.strip()
    time.sleep(1)

    descripcion_larga=container.find('div',itemprop="description")
    if descripcion_larga:
        total_lines=descripcion_larga.text.strip().strip('\n').strip('\t')
        lines=total_lines.splitlines()
        product_information['DescripcionLarga']='. '.join(lines)
        
        for line in lines:
            if 'Maridaje' in line:
                product_information['Maridaje']=line[9:].strip()
            elif 'Origen' in line:
                product_information['PaisOrigen']=line[7].strip()
        time.sleep(1)

    # MARIDAJE
    # ALCVOL
    # MARCA
    # PAIS ORIGEN
    # UVA
    # TAMANO
    if product_information['DescripcionCorta'] !='':
        words=product_information['DescripcionCorta'].split()
        
        product_information['Tamaño']=words[-1]
        product_information['Marca']=words[1]
    time.sleep(1)

    imagen=container.find('img')
    if imagen:
        imagen_link=URL+imagen.get('src')
        product_information['Img']=imagen_link
    time.sleep(1)

    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://laduenamx.com'
    
    driver.get(link)
    time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(id="shopify-section-collection-template")
    pagination_html=main_body.find('div',class_="pagination grid__item large--three-quarters push--large--one-quarter")
            
    if pagination_html:
        pages_urls=pagination_html.find_all('a')
        last_page=pages_urls[-2].get('href')[-1]
        for i in range(1,int(last_page)+1):
            page_link=link+f'?page={i}'
            pages.append(page_link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver, fecha):
    INFORMANTE = 'La Dueña'
    URL = 'https://laduenamx.com'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="top_links_wrapper")
    
    itemslevel0=menu.find('ul').find_all('li',recursive=False)
    counter=0
    total_pages=0
    for itemlevel0 in itemslevel0:
        categoria=itemlevel0.find('a').get_text().strip().strip('\n')
        menulevel1=itemlevel0.find('ul')

        if menulevel1:
            itemslevel1=menulevel1.find_all('li',recursive=False)
        else:
            itemslevel1=[itemlevel0]

        for itemlevel1 in itemslevel1:

            categoria_tipo=itemlevel1.find('a').get_text()
            print(categoria_tipo)
            link=URL+itemlevel1.find('a').get('href')

            pages=pagination(driver,link)
            total_pages+=len(pages)
            for page in pages:
                driver.get(page)
                time.sleep(5)
                page_html=BeautifulSoup(driver.page_source,'html.parser')
                main_body=page_html.find(id="shopify-section-collection-template")
                product_section=main_body.find('div',class_="grid__item large--three-quarters collection-main-body")
                products=product_section.find_all('p',class_="product-grid--title")
                for product in products:
                    product_link=URL+product.find('a').get('href')
                    time.sleep(5)
                    driver.get(product_link)

            
                    producto=agregar_informacion(
                        BeautifulSoup(driver.page_source, 'html.parser'),
                        INFORMANTE,categoria,categoria_tipo,fecha)
                    
                    informacion.append(producto)
                    counter+=1
                    print(counter)
    print(total_pages)
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

    datos=productos_vinos(driver,stamped_today)
    filename='laduena_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)

    driver.quit()

    print(f"{time.time()-inicio}")

