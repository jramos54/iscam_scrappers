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
    

def agregar_informacion(soup,informante,categoria,fecha):
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
    container=soup.find('div',class_="page-wrap").find('div',class_="page-area")
    if container:
        descripcion_corta=container.find('div',class_="summary entry-summary").find('h1')
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text

        # descripcion_larga=container.find('table',class_="woocommerce-product-attributes shop_attributes").text
        # descripcion_larga_=descripcion_larga.splitlines()
        # if descripcion_larga:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']

        # sku=container.find('span',class_="sku")
        # if sku:
        #     product_information['SKU']=sku.text

        imagen_element=container.find('figure',class_="woocommerce-product-gallery__wrapper")
        imagen=imagen_element.find('img')
        if imagen:
            product_information['Img']=imagen.get('src')

        precio=container.find('div',class_="summary entry-summary").find('p',class_="price")
        if precio:
            product_information['Precio']=precio.text.strip()
        
        etiqueta=container.find('span',class_="posted_in")
        if etiqueta:
            product_information['Etiqueta']=etiqueta.find('a').text

        # json_prod=json.dumps(product_information,indent=4)
        # print(json_prod)

    return product_information


def pagination(driver,link):
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('ul',class_="page-numbers")

    pages.append(link)

    if pagination_html:
        paginas=pagination_html.find_all('li')
        last_page_link=paginas[-1].find('a').get('href')
        
        last_page=int(last_page_link.strip().split('/')[-2])
        
        for i in range(2,last_page+1):
            pages.append(link+'/page/'+f'{i}'+'/')

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papeleria la Palma'
    URL = 'https://papelerialapalma.com/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find('div',class_="page-wrap")
    
    lista_level0=menu.find(id="text-5")
    itemslevel0=lista_level0.find_all('a',recursive=True)

    counter=0
    for itemlevel0 in itemslevel0:
        categoria=itemlevel0.text
        # print(itemlevel0.find('span').text)
        # print('-'*40)
        link=itemlevel0.get('href')
        print(categoria)
        if categoria=='Nuevos':
            continue
        pages=pagination(driver,link)
        
        for page in pages:
            driver.get(page)
            page_html=BeautifulSoup(driver.page_source,'html.parser')

            products_content=page_html.find('ul',class_="products columns-4")
            if products_content:
                products=products_content.find_all('li')

                for product in products:
                    
                    product_link=product.find('a',class_='woocommerce-LoopProduct-link woocommerce-loop-product__link')
                    
                    # print(product_link.get('href'))
                    driver.get(product_link.get('href'))
                    
                    producto=agregar_informacion(
                        BeautifulSoup(driver.page_source, 'html.parser'),
                        INFORMANTE,categoria,fecha)
                    informacion.append(producto)
                    counter+=1
                    print(counter)
    return informacion            

def main(driver,stamped_today):
    # Se toma el argumento del directorio destino
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()

    # Ejecucion normal del script
    datos=productos_papelera(driver,stamped_today)      
    filename=args.ruta + 'Papelerialapalma_productos_'+stamped_today+'.csv' 
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

    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)


    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    

    main(driver,stamped_today)
    
    driver.quit()

    print(f"{time.time()-inicio}")

