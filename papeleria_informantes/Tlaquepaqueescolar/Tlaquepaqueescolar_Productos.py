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
    URL='https://www.tlaquepaqueescolar.com.mx/Te2023/'
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
    
    descripcion_corta=soup.find('h3')
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text.strip()
        product_information['DescripcionLarga']=descripcion_corta.text.strip()

    # descripcion_larga=soup.find('p',class_="text-justify")
    # if descripcion_larga:
    #     product_information['DescripcionLarga']=descripcion_larga.text

    sku=soup.find_all('div')
    if sku:
        product_information['SKU']=sku[-1].text[9:]

    imagen=soup.find('img')
    if imagen:
        product_information['Img']=URL+imagen.get('src')

    # precio=soup.find('h2',class_='text-primary')
    # if precio:
    #     product_information['Precio']=precio.text.strip()

    # json_prod=json.dumps(product_information,indent=4)
    # print(json_prod)
    if product_information['SKU'] =="" and product_information['DescripcionCorta']=='':
        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)
        return None

    return product_information

def extract_products(container):
    container_1 = container.find('div')
    container_2 = container_1.find_all('div', recursive=False)
    products = container_2[-1].find_all('div', recursive=False)
    return products

def process_category(driver, category_url, informacion, INFORMANTE, categoria, fecha,URL):
    driver.get(category_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    container = soup.find(id="section-5")
    products = extract_products(container)

    for product in products:
        subcat = product.find('a')
        if subcat:
            link_target = subcat.get('href')
            link = URL + link_target
            process_category(driver, link, informacion, INFORMANTE, categoria,fecha,URL)
        else:
            producto = agregar_informacion(
                product,
                INFORMANTE, categoria, fecha)
            if producto:
                informacion.append(producto)
            # counter += 1
            # print(counter)




def productos_papelera(driver, fecha):
    INFORMANTE = 'Tlaquepaque Escolar'
    URL_escolar = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogoescolar.html'
    URL_oficina = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogooficinas.html'
    URL='https://www.tlaquepaqueescolar.com.mx/Te2023/'
    informacion = []
    urls=[URL_escolar,URL_oficina]
    counter=0
    for url in urls:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        menu = soup.find(id="section-5")
        itemslevel0=menu.find_all('a',recursive=True)

#######################################################################
        for itemlevel0 in itemslevel0:
            categoria = itemlevel0.text
            print(categoria)
            link_target = itemlevel0.get('href')
            link = URL + link_target
            process_category(driver, link, informacion, INFORMANTE,categoria, fecha,URL)        
        for itemlevel0 in itemslevel0:
            categoria=itemlevel0.text
            print(categoria)
            link_target=itemlevel0.get('href')
            link=URL+link_target
            driver.get(link)
            
            soup=BeautifulSoup(driver.page_source, 'html.parser')
            container=soup.find(id="section-5")
            # print(container)

            container_1=container.find('div')
            # products=container.find_all('div',class_="col-md-4 section-5-box wow fadeInUp")
            container_2=container_1.find_all('div',recursive=False)

            # print(container_2[-1])
            products=container_2[-1].find_all('div',recursive=False)
            
            for product in products:

                subcat=product.find('a')
                if subcat:
                    link_target=subcat.get('href')
                    link=URL+link_target

                    driver.get(link)
                    soup=BeautifulSoup(driver.page_source, 'html.parser')
                    container=soup.find(id="section-5")
                    container_1=container.find('div')
                    container_2=container_1.find_all('div',recursive=False)
                    productos=container_2[-1].find_all('div',recursive=False)
                    for item in productos:
                        producto=agregar_informacion(
                            item,
                            INFORMANTE,categoria,fecha)
                        informacion.append(producto)
                        counter+=1
                        print(counter)
                else:
                    producto=agregar_informacion(
                        product,
                        INFORMANTE,categoria,fecha)
                    informacion.append(producto)
                    counter+=1
                    print(counter)

    return informacion            
                

if __name__=='__main__':
    URL_escolar = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogoescolar.html'
    URL_oficina = 'https://www.tlaquepaqueescolar.com.mx/Te2023/catalogooficinas.html'
    
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

    response=requests.get(URL_escolar)
    
    if response.status_code==200:
        datos=productos_papelera(driver,stamped_today)
        filename='Tlaquepaque_productos_'+stamped_today+'.csv'
        exportar_csv(datos,filename)
    else:
        print('sin conexion')
    driver.quit()

    print(f"{time.time()-inicio}")

