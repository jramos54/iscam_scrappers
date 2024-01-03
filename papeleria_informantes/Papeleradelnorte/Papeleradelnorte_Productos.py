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
    container=soup.find('section')
    descripcion_corta=container.find_all('h4')
    complemento=container.find('h5')
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta[1].text + ' ' + complemento.text

    descripcion_larga=soup.find('p',class_="text-justify")
    if descripcion_larga:
        product_information['DescripcionLarga']=descripcion_larga.text

    # form=soup.find('form',class_='form-inline')
    # sku=form.find('p')
    # if sku:
    #     product_information['SKU']=sku.text[4:].strip()

    imagen=soup.find('img',id="stand-product-img")
    if imagen:
        product_information['Img']=imagen.get('src')

    precio=soup.find('h2',class_='text-primary')
    if precio:
        product_information['Precio']=precio.text.strip()

    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://www.papeleradelnorte.com.mx/'
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('div',class_='cx-pagination')
    
    if pagination_html:
        pages_urls=pagination_html.find_all('a')
        if pages_urls:
            for page_url in pages_urls:
                pages.append(URL+page_url.get('href'))
        else:
            pages.append(link)

    return tuple(set(pages))


def links_categorias(soup):
    print("obteniendo categorias...")
    informacion=[]
    menu = soup.find('ul',class_='nav navbar-nav')
    itemslevel0=menu.find_all('li',recursive=False)

    for itemlevel0 in itemslevel0:
                
        menulevel1=itemlevel0.find('ul')
        itemslevel1=menulevel1.find_all('li',recursive=False)
        
        for itemlevel1 in itemslevel1:
            
            menulevel2=itemlevel1.find('ul')
            itemslevel2=menulevel2.find_all('li',recursive=False)
            
            for itemlevel2 in itemslevel2:
                #print(itemlevel2.find('a').get_text())
                categoria=itemlevel2.find('a').get_text()
                link=itemlevel2.find('a').get('href')
                #print(link)
                #pages=pagination(driver,link)
                informacion.append((categoria,link))
    return informacion


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papelera del Norte'
    URL = 'https://www.papeleradelnorte.com.mx/'
    informacion = []

    driver.get(URL)
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    links_categories=links_categorias(soup)
    counter=0

    urls=[]
    for category in links_categories:
        categoria=category[0]
        print(f"obteniendo links de categoria --> {categoria}")
        
        link=category[-1]    
        product_links=links_productos(link)
        urls.append((categoria,product_links))
        
    for url in urls:
        categoria=url[0]
        links_products=url[-1]
        for link in links_products:
            try:
                driver.get(link)
                time.sleep(3)
                producto=agregar_informacion(BeautifulSoup(driver.page_source, 'html.parser'),INFORMANTE,categoria,fecha)
                informacion.append(producto)
                counter+=1
                print(counter)
            except Exception as e:
                print('-'*50)
                print(e)
                print('-'*50)
                print(link)
                print('-'*50)
                time.sleep(5)
                driver.quit()
                driver = iniciar_driver()
                time.sleep(5)
                
    return informacion            

def links_productos(link):
    product_links=[]
    driver.get(link)
    time.sleep(3)
    page_html=BeautifulSoup(driver.page_source,'html.parser')
    products=page_html.find('div',class_="col-lg-8 col-sm-6").find_all('h4')
    for product in products:
        product_link=product.find('a')
        product_links.append(product_link.get('href'))
    return product_links

def sucursales_papelera(driver,fecha):
  
    INFORMANTE = 'Papelera del Norte'
    URL = 'https://www.papeleradelnorte.com.mx/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu=soup.find('div',id='modal-sucursales')
    sitios=menu.find('div',class_='list-group')
    directorio=[]  

    for sitio in sitios:
        
        tienda={
            'Informante':INFORMANTE,
            'Sucursal':'',
            'Direccion':'',
            'CP':'',
            'Latitud':'',
            'Longitud':'',
            'fecha':fecha
        }

        if sitio:

            ubicacion=sitio.text
            
            if len(ubicacion)>1:
                
                tiendas=ubicacion.splitlines()
                tiendas=tiendas[4:]
                sucursal=tiendas.pop(0)
                if sucursal:
                    tienda['Sucursal']=sucursal

                direccion=tiendas.pop(1)
                if direccion:
                    
                    tienda['Direccion']=direccion
                    tienda['CP']=obtencion_cp(direccion)
                    
                    longitud,latitud = geolocalizacion(tienda['Direccion'])
                    tienda['Latitud'] = latitud
                    tienda['Longitud'] = longitud

                    # json_dato=json.dumps(tienda,indent=4)
                    # print(json_dato)

                    directorio.append(tienda)

    return directorio
    

def iniciar_driver():
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)
    return driver

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

    datos=productos_papelera(driver,stamped_today)
    filename='Papeleradelnorte_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    datos=sucursales_papelera(driver,stamped_today)
    filename='papeleradelnorte_sucursales_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")

