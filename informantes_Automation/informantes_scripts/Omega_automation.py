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
    

def agregar_informacion(soup,informante,fecha):
    product_information = {
        'Informante': informante,
        'Categoria': '',
        'DescripcionCorta': '',
        'DescripcionLarga': '',
        'SKU': '',
        'Etiqueta': '',
        'Img': '',
        'Precio': '',
        'Fecha': fecha
        }
    
    container=soup.find('div',class_="pb-right-column col-xs-12 col-sm-6")
    if container:
        descripcion_corta=container.find('h1')
        if descripcion_corta:
            descripcion_corta_=descripcion_corta.text.strip()
            product_information['DescripcionCorta']=descripcion_corta_.strip('"')

        table_rows=container.find_all('tr')

        descripcion_larga=table_rows[-1].find_all('td')
        descripcion_larga_=descripcion_larga[-1]
        if descripcion_larga[0].text== 'Datos adicionales:':
            texto_descripcion=descripcion_larga_.text.strip()
            lineas_descripcion=texto_descripcion.splitlines()
            product_information['DescripcionLarga']='. '.join(lineas_descripcion)
        else:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']

        sku=table_rows[0].find_all('td')
        sku_=sku[-1]
        if sku:
            product_information['SKU']=sku_.text.strip('#')

        categoria=table_rows[4].find_all('td')
        categoria_=categoria[-1]
        if categoria:
            product_information['Categoria']=categoria_.text.strip()

        imagen_element=soup.find('div',class_="pb-left-column col-xs-12 col-sm-6")
        imagen=imagen_element.find('img')
        if imagen:
            link_imagen=imagen.get('src').replace('\\','/')
            product_information['Img']=link_imagen.split()[0]

        etiqueta=table_rows[3].find_all('td')
        etiqueta_=etiqueta[-1]
        if etiqueta:
            product_information['Etiqueta']=etiqueta_.text.strip()

        # precio=soup.find('h2',class_='text-primary')
        # if precio:
        #     product_information['Precio']=precio.text.strip()

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://www.papeleriaomega.com.mx/'
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('div',class_="col-md-12")
    # pages.append(link)

    if pagination_html:
        text_articles=pagination_html.text
        text_pages=text_articles.split(' ')
        if text_pages[-3].isdigit():
            num_articles=int(text_pages[-3])
            total_pages=(num_articles//100)+1
            for i in range(1,total_pages+1):
                url_link=URL+f'busqueda?displayResults=grid&pagina={i}&words=&orderBy=&paginado=100&category={link[-1]}&subcategory='
                pages.append(url_link)

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papeleria Omega'
    URL = 'https://www.papeleriaomega.com.mx/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find('ul',class_="vertical-menu-list")
    
    itemslevel0=menu.find_all('li',recursive=False)

    counter=0
    for itemlevel0 in itemslevel0:
        link_level0=itemlevel0.find('a')
        pages=pagination(driver,link_level0.get('href'))
       
        for page in pages:
            driver.get(page)
            page_html=BeautifulSoup(driver.page_source,'html.parser')
            product_list=page_html.find(id="view-product-list")
            if product_list:

                products_content=product_list.find('ul',class_="row product-list grid")
                if products_content:
                    products=products_content.find_all('li')

                    for product in products:
                        
                        product_link=product.find('a')
                        # print(product_link.get('href'))
                        driver.get(product_link.get('href'))
                        
                        producto=agregar_informacion(
                            BeautifulSoup(driver.page_source, 'html.parser'),
                            INFORMANTE,fecha)
                        informacion.append(producto)
                        counter+=1
                        print(counter)
    return informacion            

def main(driver,stamped_today):
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args() 
    
    datos=productos_papelera(driver,stamped_today)
    filename=args.ruta + 'Omega_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
               

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
    chrome_options.add_argument('--js-flags=--max-old-space-size=4096')
    
    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")


    main(driver,stamped_today)
    driver.quit()

    print(f"{time.time()-inicio}")

