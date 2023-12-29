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
    container=soup.find(id='main')
    if container:
        descripcion_corta=container.find('h1')
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text

        descripcion_larga=container.find('table',class_="woocommerce-product-attributes shop_attributes").text
        descripcion_larga_=descripcion_larga.splitlines()
        if descripcion_larga:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']+'. '.join(elemento for elemento in descripcion_larga_ if elemento.strip() != '')

        sku=container.find('span',class_="sku")
        if sku:
            product_information['SKU']=sku.text

        imagen_element=container.find('li')
        imagen=imagen_element.find('img')
        if imagen:
            product_information['Img']=imagen.get('src')

        # precio=soup.find('h2',class_='text-primary')
        # if precio:
        #     product_information['Precio']=precio.text.strip()

        # json_prod=json.dumps(product_information,indent=4)
        # print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://superpapelera.com.mx/'
    
    driver.get(link)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    pagination_html=soup.find('div',class_='shoptimizer-sorting sorting-end')

    pages.append(link)

    if pagination_html:
        total_articles=soup.find('p',class_="woocommerce-result-count")
    
        text_articles=total_articles.text
        text_pages=text_articles.split(' ')
        text_pages.pop()
        if text_pages[-1].isdigit():
            num_articles=int(text_pages[-1])
            total_pages=(num_articles//12)+1
            for i in range(2,total_pages+1):
                pages.append(link+'/page/'+f'{i}'+'/')

    return tuple(set(pages))


def productos_papelera(driver, fecha):
    INFORMANTE = 'Super Papelera'
    URL = 'https://superpapelera.com.mx/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find('li',id="nav-menu-item-10787")
    
    lista_level0=menu.find('ul')
    itemslevel0=lista_level0.find_all('li',recursive=False)

    counter=0
    for itemlevel0 in itemslevel0:
        
        # print(itemlevel0.find('span').text)
        # print('-'*40)
        
        lista_level1=itemlevel0.find('ul')
        itemslevel1=lista_level1.find_all('li',recursive=False)

        for itemlevel1 in itemslevel1:
            # print(itemlevel1.find('span').text)
            # print('-  - '*10)

            menulevel2=itemlevel1.find('ul')
            itemslevel2=menulevel2.find_all('li',recursive=False)
            
            for itemlevel2 in itemslevel2:                
                categoria=itemlevel2.find('span').get_text()
                link=itemlevel2.find('a').get('href')
                print(categoria)
                # print(link)
                pages=pagination(driver,link)
                
                for page in pages:
                    driver.get(page)
                    page_html=BeautifulSoup(driver.page_source,'html.parser')

                    products_content=page_html.find('ul',class_="products columns-3")
                    if products_content:
                        products=products_content.find_all('li')

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
    return informacion            


def sucursales_superpapelera(driver,fecha):

    INFORMANTE = 'Super Papelera'
    URL = 'https://superpapelera.com.mx/sucursales/'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu=soup.find(id='main')
    sitios=menu.find_all('h3',class_='elementor-heading-title elementor-size-medium')
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
            parent=sitio.parent.parent
            ubicacion=parent.find_next_sibling().text
            sucursal=sitio.text

            direccion=ubicacion.strip()

            if sucursal:
                tienda['Sucursal']=sucursal
            
            if direccion:
                if direccion[-5:].isdigit():
                    tienda['Direccion']=direccion[:-6]+' CP '+direccion[-5:]
                else:tienda['Direccion']=direccion
                tienda['CP']=obtencion_cp(tienda['Direccion'])
                
                longitud,latitud = geolocalizacion(tienda['Direccion'])
                tienda['Latitud'] = latitud
                tienda['Longitud'] = longitud

                json_dato=json.dumps(tienda,indent=4)
                print(json_dato)

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

    datos=productos_papelera(driver,stamped_today)
    filename='Superpapelera_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    datos=sucursales_superpapelera(driver,stamped_today)
    filename='superpapelera_sucursales_'+stamped_today+'.csv'
    exportar_csv(datos,filename)

    # link='https://superpapelera.com.mx/escolar/utiles-escolares/cuadernos-blocks-y-libretas/'
    # for i in pagination(driver,link):
    #     response=requests.get(i)
    #     print(response.status_code)
    
    driver.quit()

    print(f"{time.time()-inicio}")

