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
    container=soup.find(id="content")

    if container:
        descripcion_corta=container.find('h1')
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text

        descripcion_larga=container.find('div',class_="col-sm-4").find('li').text
        descripcion_tab=container.find(id="tab-description").text
        descripcion_larga_=descripcion_larga + ' .' + descripcion_tab
        if descripcion_larga:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']+'. '+descripcion_larga_

        sku=container.find('h3').text
        if sku:
            sku_=sku.split()
            product_information['SKU']=sku_[-1]

        imagen_element=container.find('div',class_="col-sm-8").find('li')
        imagen=imagen_element.find('a')
        if imagen:
            product_information['Img']=imagen.get('href')

        precio=container.find('div',class_="col-sm-4").find('h2')
        if precio:
            product_information['Precio']=precio.text.strip()

        # json_prod=json.dumps(product_information,indent=4)
        # print(json_prod)

    return product_information


def pagination(driver,link):
   
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('ul',class_="pagination")
    pages.append(link)

    if pagination_html:
        paginas=pagination_html.find_all('li')
        last_page_link=paginas[-1].find('a').get('href')
        last_page=int(last_page_link.split('=')[-1])
        
        for i in range(2,last_page+1):
            pages.append(link+'&page='+f'{i}')

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Papeleria Cornejo'
    URL = 'https://www.papeleriacornejo.com/pc/index.php?route=common/home'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="menu")
    
    lista_level0=menu.find('ul')
    itemslevel0=lista_level0.find_all('li',recursive=False)

    counter=0
    for itemlevel0 in itemslevel0:
        
        # print(itemlevel0.find('a').text)
        # print('-'*40)
        
        lista_level1=itemlevel0.find('ul')
        if lista_level1:
            itemslevel1=lista_level1.find_all('li',recursive=False)
        else:
            continue
        
        for itemlevel1 in itemslevel1:
            # print(itemlevel1.find('a').text)
            # print('-  - '*10)
            categoria=itemlevel1.find('a').text
            link=itemlevel1.find('a').get('href')
            driver.get(link)
            page_html=BeautifulSoup(driver.page_source,'html.parser')
            body=page_html.find(id="content")
            itemslevel2=body.find_all('li')
            body_items=body.find_all('div',class_="caption")
            
            for itemlevel2 in itemslevel2:                
                categoria=itemlevel2.find('a').get_text()
                link=itemlevel2.find('a').get('href')
                print(categoria)
                # print(link)
                pages=pagination(driver,link)
                
                for page in pages:
                    driver.get(page)
                    page_html=BeautifulSoup(driver.page_source,'html.parser')

                    products=page_html.find_all('div',class_="caption")
                    for product in products:
                            
                        product_link=product.find('a')
                        # print(product_link.get('href'))
                        driver.get(product_link.get('href'))
                        
                        producto=agregar_informacion(
                            BeautifulSoup(driver.page_source, 'html.parser'),
                            INFORMANTE,categoria,fecha)
                        informacion.append(producto)
                        counter+=1
                        print(counter)
            
            for product in body_items:
                            
                        product_link=product.find('a')
                        # print(product_link.get('href'))
                        driver.get(product_link.get('href'))
                        
                        producto=agregar_informacion(
                            BeautifulSoup(driver.page_source, 'html.parser'),
                            INFORMANTE,categoria,fecha)
                        informacion.append(producto)
                        counter+=1
                        print(counter) 
    return informacion            


def sucursales_cornejo(driver,fecha):

    INFORMANTE = 'Papeleria Cornejo'
    URL = 'https://www.papeleriacornejo.com/pc/index.php?route=information/contact'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu=soup.find(id="content")
    sitios=menu.find_all('div',class_='row')
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
            ubicacion=sitio.find('address').text
            sucursal=sitio.find('strong')

            direccion=ubicacion.strip().splitlines()
            if sucursal:
                tienda['Sucursal']=sucursal.text
            
            if direccion:
                tienda['Direccion']='. '.join(elemento for elemento in direccion if '@' not in elemento)
                tienda['CP']=obtencion_cp(tienda['Direccion'])
                
                longitud,latitud = geolocalizacion(tienda['Direccion'])
                tienda['Latitud'] = latitud
                tienda['Longitud'] = longitud

                # json_dato=json.dumps(tienda,indent=4)
                # print(json_dato)

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
    chrome_options.add_argument('--js-flags=--max-old-space-size=4096')
    
    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_papelera(driver,stamped_today)
    filename='Papeleriacornejo_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)

    datos_sucursal=sucursales_cornejo(driver,stamped_today)
    filename='Papeleriacornejo_sucursales_'+stamped_today+'.csv'

    exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")

