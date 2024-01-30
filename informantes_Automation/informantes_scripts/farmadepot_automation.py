
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


def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto


def agregar_informacion(soup,informante,categoria,fecha):
    URL = ''
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Img':'',
        'Fecha':fecha
        }
    container=soup.find(class_="section")
    if container:
        # SKU
        # sku=container.find('span',class_="sku")
        # if sku:
        #     sku_text=sku.text
        #     product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(itemprop="name")
        if descripcion_corta:
            caracteres_eliminar = ['-', '"', '.']
            descripcion_text=descripcion_corta.text.strip()

            product_information['DescripcionCorta']=limpiar_texto(descripcion_text,caracteres_eliminar)
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="price")
        if precio:
            precio_text=precio.text.strip()
            symbol_loc=precio_text.find('$')
            product_information['Precio']=precio_text[symbol_loc:]
        # time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="answer").find('p')
        
        if descripcion_larga:
            lines=descripcion_larga.text.splitlines()
            product_information['DescripcionLarga']=' '.join(lines).strip()
 
        # IMAGEN
        imagen_container=container.find(class_="column one-second product_image_wrapper")
        if imagen_container:
            imagen=imagen_container.find('img')
            if imagen:
                
                imagen_link=imagen.get('src')
                
                product_information['Img']=imagen_link
                
        time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = ''
    
    driver.get(link)
    time.sleep(2)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="pages")

    if main_body:
        
        pages_urls=main_body.find_all('a')
        last_page=pages_urls[-1].get('href').split('/')[-2]
        for i in range(1,int(last_page)+1):
            page_link=link+f'page/{i}/'
            pages.append(page_link)
    else:
        pages.append(link)
    

    return pages


def productos_abarrotes(driver, fecha):
    INFORMANTE = 'Farmadepot'
    URL = 'https://farmadepot.com.mx/productos/'
    BASE_URL=''
    informacion = []

    driver.get(URL)
    # time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(class_="products grid")

    categories=menu.find_all('li')
    counter=0

    for category in categories:
       
        categoria_text=category.find('h2').text.strip()
        categoria_loc=categoria_text.find('(')
        categoria=categoria_text[:categoria_loc]
        link_categoria=category.find('a').get('href')
        print(categoria)
        print(link_categoria)
        time.sleep(2)
        pages=pagination(driver,link_categoria)
        
        for page in pages:
            print(page)

            driver.get(page)
            time.sleep(2)
            html_source=driver.page_source
            soup=BeautifulSoup(html_source,'html.parser')
        
            main_container=soup.find(class_="products grid")

            products=main_container.find_all('li',recursive=False)

            for product in products:
                link_product=product.find(class_="desc").find('a')
                link=link_product.get('href')
                print(link)
                driver.get(link)
                time.sleep(2)
                dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria,fecha)
                informacion.append(dato)
                counter+=1
                print(counter)
        
    return informacion           
                


def sucursales_abarrotes(driver,fecha):
   
    INFORMANTE='Farmadepot'
    URL='https://farmadepot.com.mx/sucursales/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="Content")

    sucursales_tags=main.find_all('div',class_="team team_vertical")
    
    directorio=[]
    for sucursal in sucursales_tags:
        
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

        sucursal_texto=sucursal.find('h4')
        if sucursal_texto:
            tienda['Sucursal']=sucursal_texto.text.strip()

        direccion_texto=sucursal.find(class_="desc")
        if direccion_texto:

            direccion_lineas=direccion_texto.text.splitlines()
           
            tienda['Direccion']=' '.join(direccion_lineas[:-3])

            tienda['CP']=obtencion_cp(tienda['Direccion'])
            
            longitud,latitud = geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

        telefono=sucursal.find(class_="phone")
        if telefono:
            tienda['Telefono']=telefono.text.strip()
        directorio.append(tienda)

    return directorio

def main(driver,stamped_today):
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()
    
    datos=productos_abarrotes(driver,stamped_today)
    filename=args.ruta+'farmadepot_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    sucursal_datos=sucursales_abarrotes(driver,stamped_today)
    filename=args.ruta+'farmadepot_tiendas_'+stamped_today+'.csv'
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

