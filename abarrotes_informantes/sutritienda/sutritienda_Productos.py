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
    
    
def tamano_producto(cadena):
    match = re.search(r'\d+\s*[A-Za-z]+', cadena)
    
    if match:
        return match.group()
    else:
        return ''

def text_segments(texto,word):
    segmentos_encontrados = []
    text=texto.lower()
    inicio = 0
    alc_pos = text.find(word, inicio)

    while alc_pos != -1:
        # Buscar la posición del próximo "alc" a partir de la posición después de la última ocurrencia
        siguiente_alc_pos = text.find(word, alc_pos + 1)

        # Si no se encuentra más "alc", tomar el resto del texto
        if siguiente_alc_pos == -1:
            segmento = text[alc_pos:]
        else:
            segmento = text[alc_pos:siguiente_alc_pos]

        segmentos_encontrados.append(segmento.strip())
        inicio = alc_pos + 1
        alc_pos = text.find(word, inicio)

    return segmentos_encontrados


def agregar_informacion(soup,informante,fecha):
    URL = ''
    product_information = {
        'Informante': informante,
        'Categoria':'',
        'SKU':'',
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Marca':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    
    categoria_section=soup.find(class_="bread-crumbs")
    if categoria_section:
        categoria=categoria_section.find_all('li')
        categoria_item=categoria[-1]
        product_information['Categoria']=categoria_item.text.strip()
    
    container=soup.find(class_="product-detail")
    if container:
        # SKU
        sku=container.find('div',class_="skuReference")
        if sku:
            sku_text=sku.text
            product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product-detail__name")
        if descripcion_corta:
            caracteres_eliminar = ['-', '"', '.']
            descripcion_text=descripcion_corta.text.strip()

            product_information['DescripcionCorta']=descripcion_text
            #  # MARCA
            marca_text=product_information['DescripcionCorta'].split('-')
            if len(marca_text)>=3:
                product_information['Marca']=marca_text[-2].strip()

            # Tamano
            size=product_information['DescripcionCorta'].split('-')
            product_information['Tamaño']=tamano_producto(size[0])

        # time.sleep(1)
        
        # PRECIO
        precio=container.find(class_="productPrice")
        if precio:
            precio_text=precio.text.strip()
            symbol_loc=precio_text.find('$')
            product_information['Precio']=precio_text[symbol_loc:]
        # time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="productDescription").find('p')
        
        if descripcion_larga:
            lines=descripcion_larga.text.splitlines()
            product_information['DescripcionLarga']=' '.join(lines).strip()
 
        # IMAGEN
        imagen_container=container.find(class_="images product-detail__image")
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
    INFORMANTE = 'Sutritienda'
    URL = 'https://www.surtitienda.mx'
    BASE_URL=''
    informacion = []

    driver.get(URL)
    # time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(class_="site-nav").find('ul')

    sub_menus=menu.find_all('li',recursive=False)
    category_links=[]
    for sub_menu in sub_menus:
        menu_category=sub_menu.find('ul')
        sub_menu_categories=menu_category.find_all('li',recursive=False)
        for sub_menu_category in sub_menu_categories:
            # categoria=sub_menu_category.find('a').text
            # print(categoria)
            category_link=sub_menu_category.find('ul')
            if category_link:
                sub_categorias_links=category_link.find_all('a')
                for sub_categoria_link in sub_categorias_links:
                    url_cat=sub_categoria_link.get('href')
                    if url_cat.startswith('https://'):
                        category_url=URL+url_cat[7:]
                    else:
                        category_url=URL+url_cat
                    category_links.append(category_url)

    
    counter=0

    for category_link in category_links:
        # time.sleep(5)
        print(category_link)
        driver.get(category_link)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        product_container=soup.find(class_="prateleira vitrine")
        if product_container:
            products=product_container.find_all('div',class_="product-item")

            time.sleep(2)
    #     pages=pagination(driver,link_categoria)
        
    #     for page in pages:
    #         print(page)

    #         driver.get(page)
    #         time.sleep(2)
    #         html_source=driver.page_source
    #         soup=BeautifulSoup(html_source,'html.parser')
        
    #         main_container=soup.find(class_="products grid")

    #         products=main_container.find_all('li',recursive=False)

            for product in products:
                link_product=product.find('a',class_="dl-product-link")
                link=link_product.get('href')
                if not link.startswith('https://www.surtitienda.mx/'):
                    
                    link='https://www.surtitienda.mx/'+link[9:]

                print(link)
                driver.get(link)
                time.sleep(5)
                dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,fecha)
                if dato:
                    informacion.append(dato)
                    counter+=1
                    print(counter)
        
    return informacion           

def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto

def sucursales_abarrotes(driver,fecha):

    caracteres_eliminar = ['-', '"']

    INFORMANTE='Surtitienda'
    URL='https://www.surtitienda.mx/tiendas'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(class_="page-main--internal-page")

    sucursales_tags=main.find_all('div',class_="col-1-4 padding-20")
    
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

        sucursal_texto=sucursal.text.strip()
        if sucursal_texto:
            sucursal_lines=sucursal_texto.splitlines()
            tienda['Sucursal']=sucursal_lines[0].strip()

        
            tienda['Direccion']=limpiar_texto(sucursal_lines[-1].strip(),caracteres_eliminar)

            tienda['CP']=obtencion_cp(tienda['Direccion'])
            
            longitud,latitud = geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

        # telefono=sucursal.find(class_="phone")
        # if telefono:
        #     tienda['Telefono']=telefono.text.strip()
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

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_abarrotes(driver,stamped_today)
    filename='sutritienda_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    sucursal_datos=sucursales_abarrotes(driver,stamped_today)
    filename='sutritienda_tiendas_'+stamped_today+'.csv'
    exportar_csv(sucursal_datos,filename)
    # link='https://farmadepot.com.mx/categoria-producto/perfumeria/'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

