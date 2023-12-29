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
    

def text_segments(texto,word):
    segmentos_encontrados = []
    text=texto.lower()
    inicio = 0
    alc_pos = text.find(word, inicio)

    while alc_pos != -1:
        siguiente_alc_pos = text.find(word, alc_pos + 1)
        if siguiente_alc_pos == -1:
            segmento = text[alc_pos:]
        else:
            segmento = text[alc_pos:siguiente_alc_pos]

        segmentos_encontrados.append(segmento.strip())
        inicio = alc_pos + 1
        alc_pos = text.find(word, inicio)

    return segmentos_encontrados


def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://hscomercial.mx/'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    container=soup.find(class_="product-page-container")
    if container:
        # SKU
        sku=container.find('span',class_="sku")
        if sku:
            sku_text=sku.text
            product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product_title entry-title")
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text.strip()
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        # time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="price")
        if precio:
            product_information['Precio']=precio.text.strip()
        # time.sleep(1)

        # DESCRIPCION LARGA
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
        
        size=product_information['DescripcionCorta'].split()
        product_information['Tamaño']=size[-1]
 
        # IMAGEN
        imagen_container=container.find(class_="product-images-container")
        imagen=imagen_container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link=imagen.get('src')
                if imagen_link.startswith(URL):
                    product_information['Img']=imagen_link
                else:
                    product_information['Img']=URL+imagen_link
        # time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


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


def productos_dulces(driver, fecha):
    INFORMANTE = 'H. S. Comercial'
    URL = 'https://hscomercial.mx/dulces-mayorista-marcas-de-dulces/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="main")
    categories=menu.find_all('a')
    
    counter=0
    for category in categories:
        #
        # categoria_container=category.find(class_="has-text-align-center has-woostify-heading-6-font-size")
        categoria_container=category.find('img')
        categoria=categoria_container.get('alt')
        link_categoria=category.get('href')
        print(categoria)
        print(link_categoria)
        
        driver.get(link_categoria)
        html_source=driver.page_source
        soup=BeautifulSoup(html_source,'html.parser')
        
        main_container=soup.find(id="main")
        main_list=main_container.find('ul',class_="products columns-4 tablet-columns-4 mobile-columns-2")
        products=main_list.find_all('li')

        for product in products:
            link=product.find('a')
            driver.get(link.get('href'))
            dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria,fecha)
            informacion.append(dato)
            counter+=1
            print(counter)
        
    return informacion           
                

def sucursales_dulces(driver,fecha):
    
    INFORMANTE='H.S. Comercial'
    URL='https://hscomercial.mx/sucursal2021/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="main")

    sucursales=main.find_all('div',class_="wp-block-media-text__content")
    directorio=[]

    print(len(sucursales))

    for sucursal in sucursales:
        
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'Telefono':'',
            'Email':'',
            'fecha':fecha
        }

        sucursal_texto=sucursal.text
        sucursal_lineas=sucursal_texto.splitlines()
        sucursal_lineas.pop(0)
        tienda['Sucursal']=sucursal_lineas.pop(0)

        for linea in sucursal_lineas:
            if '@' in linea:
                tienda['Email']=linea
            elif 'tel' in linea.lower():

                tienda['Telefono']=linea[6:]
            else:
                tienda['Direccion']+=linea + ' '

        tienda['CP']=obtencion_cp(tienda['Direccion'])
        
        longitud,latitud = geolocalizacion(tienda['Direccion'])
        tienda['Latitud'] = latitud
        tienda['Longitud'] = longitud

        directorio.append(tienda)

    return directorio


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

    datos=productos_dulces(driver,stamped_today)
    filename='hscomercial_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    sucursal_datos=sucursales_dulces(driver,stamped_today)
    filename='hscomercial_tiendas_'+stamped_today+'.csv'
    exportar_csv(sucursal_datos,filename)
    
    

    driver.quit()

    print(f"{time.time()-inicio}")

