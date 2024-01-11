
import os,datetime,json,time,requests,csv,re
import googlemaps

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

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

    descripcion_corta=soup.find('h1',class_="page-title")
    if descripcion_corta:
        descripcion_corta_=descripcion_corta.get_text().splitlines()
        texto_descripcion=descripcion_corta_[-1].strip(' ').strip('"')
        product_information['DescripcionCorta']=texto_descripcion.replace('\\','')
    
    descripcion_larga=soup.find('table',class_="data table additional-attributes")
    if descripcion_larga:
        descripcion_larga_=descripcion_larga.get_text().splitlines()
        product_information['DescripcionLarga']=product_information['DescripcionCorta']+'. '.join(elemento for elemento in descripcion_larga_ if elemento.strip() != '')
    
    precio=soup.find('span',class_="price")
    if precio:
        product_information['Precio']=precio.get_text()
    
    sku=soup.find('div',class_="product attribute sku")
    if sku:
        sku_=sku.get_text().splitlines()
        product_information['SKU']=sku_[-1].strip(' ')
    
    imagen=soup.find('img',class_="fotorama__img")
    if imagen:
        product_information['Img']=imagen.get('src')

    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://www.adosa.com.mx/'
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('div',class_='pages')
    
    pages.append(link)

    if pagination_html:
        total_articles=soup.find('p',id="toolbar-amount")
        
        text_articles=total_articles.text
        text_pages=text_articles.split(' ')
        text_pages.pop()
        num_articles=int(text_pages[-1])
        total_pages=(num_articles//30)+1
        for i in range(2,total_pages+1):
            pages.append(link+'?p='+f'{i}')

        
    return tuple(set(pages))


def productos_adosa(driver, fecha):
    INFORMANTE = 'ADOSA'
    URL = 'https://www.adosa.com.mx/'
    informacion = []

    driver.get(URL)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(class_="navigation")
    items_level0=menu.find_all('li')
    
    counter=0
    for item_level0 in items_level0:
        #
        title=item_level0.find('a')
        # print(title.get('title'))

        menu_level1=item_level0.find('div',class_="item-content1 hidden-xs hidden-sm")                
        containers_level1 = menu_level1.find_all('div',recursive=False)

        for container_level1 in containers_level1:
            items_level1=container_level1.find_all('div',recursive=False)
            for item_level1 in items_level1:
                categoria=item_level1.find('a')
                containers_level2=item_level1.find_all('div',class_="item-content1 hidden-xs hidden-sm")
               
                if containers_level2:
                    for container_level2 in containers_level2:
                        items_level2=container_level2.find_next().find_all('div')
                        
                        for item_level2 in items_level2:
                            categoria=item_level2.find('a')
                            link_page=categoria.get('href')
                            #paginacion de la categoria
                            pages=pagination(driver,link_page)
                            print(categoria.get_text())
# Comienza la extraccion por producto
                            for page in pages:
                                driver.get(page)
                                html_source=driver.page_source
                                soup=BeautifulSoup(html_source,'html.parser')
                                products=soup.find_all('li',class_="item product product-item")
                                for product in products:
                                    link=product.find('a')
                                    driver.get(link.get('href'))
                                    dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria.get_text(),fecha)
                                    informacion.append(dato)
                                    counter+=1
                                    print(counter)
                else:
                    print(categoria.get('title'))
                    driver.get(categoria.get('href'))
                    link_page=categoria.get('href')
                    pages=pagination(driver,link_page)
# Comienza la extraccion por producto
                    for page in pages:
                        driver.get(page)
                        html_source=driver.page_source
                        soup=BeautifulSoup(html_source,'html.parser')
                        products=soup.find_all('li',class_="item product product-item")
                        for product in products:
                            link=product.find('a')
                            driver.get(link.get('href'))
                            dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria.get_text(),fecha)
                            informacion.append(dato)
                            counter+=1
                            print(counter)
    return informacion


def sucursales_adosa(driver,fecha):
    """
    Funcion para el informante ifp03, ADOSA
    """
    INFORMANTE='ADOSA'
    URL='https://www.adosa.com.mx/sucursales'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find('main')

    sucursales=main.find_all('div',class_="pagebuilder-column")
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
            'fecha':fecha
        }

        nombre=sucursal.find(attrs={"data-content-type": "heading"})
        if nombre:
            tienda['Sucursal']=nombre.get_text()
        direccion=sucursal.find(attrs={"data-content-type": "text"})
        if direccion:
            direccion_=direccion.get_text()
            tienda['Direccion']=direccion_.splitlines()[0]
            tienda['CP']=obtencion_cp(tienda['Direccion'])
            directorio.append(tienda)
            longitud,latitud = geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

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

    datos=productos_adosa(driver,stamped_today)
    filename='adosa_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    sucursal_datos=sucursales_adosa(driver,stamped_today)
    filename='adosa_tiendas_'+stamped_today+'.csv'
    exportar_csv(sucursal_datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")

    