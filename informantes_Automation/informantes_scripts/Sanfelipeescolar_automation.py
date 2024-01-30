import os,datetime,json,time,requests,re,csv,argparse

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


def sucursales_sanfelipeescolar(driver,fecha):
    
    INFORMANTE='San Felipe Escolar'
    URL='https://online.sanfelipeescolar.com.mx/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    ids={"MENUDEO_ID":'05d14c0',
        "MAYOREO_ID":'7ba0184'}

    directorio=[]

    sucursal_container=soup.find(class_="elementor-element elementor-element-85c3de0 e-flex e-con-boxed e-con e-parent")
    ecoinner=sucursal_container.find('div').find('div')
    
    datas=ecoinner.find_all('div', recursive=False)
    
    for data in datas:
        lineas=data.find_all('p')
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }
        direccion=''
        for i,linea in enumerate(lineas):
            
            if i==0:
                tienda['Sucursal']=linea.get_text()
            else:
                direccion+=linea.get_text()+'\n'

        tienda['Direccion']=direccion.splitlines()[0][9:]
        tienda['CP']=obtencion_cp(direccion)
        longitud,latitud = geolocalizacion(tienda['Direccion'])
        tienda['Latitud'] = latitud
        tienda['Longitud'] = longitud
        directorio.append(tienda)

    return directorio


def productos_sanfelipeescolar(driver, fecha):
    INFORMANTE = 'San Felipe Escolar'
    URL = 'https://online.sanfelipeescolar.com.mx/'
    informacion = []

    contador=0

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="menu-item-23")
    menu_items = menu.select('.ct-menu-link')

    for item in menu_items:
        if item.get('href') != '#':
            categoria = item.get_text()
            link = item.get('href')

            driver.get(link)
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')
            product_list = soup.find('ul', {'data-products': 'type-1'})

            if product_list is not None:
                products = product_list.find_all('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link')

                for product in products:
                    product_information = {
                        'Informante': INFORMANTE,
                        'Categoria': categoria,
                        'DescripcionCorta': '',
                        'DescripcionLarga': '',
                        'SKU': '',
                        'Etiqueta': '',
                        'Img': '',
                        'Precio': '',
                        'Fecha': fecha
                    }
  
                    driver.get(product.get('href'))
                    html_product = driver.page_source
                    soup = BeautifulSoup(html_product, 'html.parser')
                    product_details = soup.find('div', class_='product-entry-wrapper')

                    descripcion_corta = product_details.find('h1', class_='product_title entry-title')
                    if descripcion_corta:
                        product_information['DescripcionCorta'] = descripcion_corta.get_text()

                    descripcion_larga = product_details.find('div', class_='woocommerce-product-details__short-description')
                    if descripcion_larga:
                        descripcion_larga_= descripcion_larga.get_text()
                        product_information['DescripcionLarga'] = ". ".join(descripcion_larga_.splitlines())

                    sku = product_details.find('span', class_='sku')
                    if sku:
                        product_information['SKU'] = sku.get_text()

                    etiqueta = product_details.find('span', class_='tagged_as')
                    if etiqueta:
                        product_information['Etiqueta'] = etiqueta.get_text()

                    precio = product_details.find('p', class_='price')
                    if precio:
                        product_information['Precio'] = precio.get_text()

                    imagen = product_details.find('a', class_='ct-image-container')
                    if imagen:
                        product_information['Img'] = imagen.get('href')
                    
                    contador+=1
                    print(contador)
                    informacion.append(product_information)

    return informacion

def main(driver,stamped_today):
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()
    
    datos=productos_sanfelipeescolar(driver,stamped_today)
    filename=args.ruta+'sanfelipeescolar_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    sucursal_datos=sucursales_sanfelipeescolar(driver,stamped_today)
    filename=args.ruta+'sanfelipeescolar_tiendas_'+stamped_today+'.csv'
    exportar_csv(sucursal_datos,filename)

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

    main(driver,stamped_today)
    
    driver.quit()

    print(f"{time.time()-inicio}")