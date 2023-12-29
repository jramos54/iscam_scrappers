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

def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://lcgroup.com.pe'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Tipo':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Maridaje':'',
        'AlcVol':'',
        'Marca':'',
        'PaisOrigen':'',
        'Uva':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
                      
            
    product_container=soup.find(id="shopify-section-template--product")
    if product_container:
        
        tipo_item=soup.find(class_="breadcrumb")
        if tipo_item:
            nav_item=tipo_item.find_all('a')
            if len(nav_item)>1:
                product_information['Tipo']=nav_item[1].text.strip()
            else:
                elements_nav=tipo_item.text
                nav_segment=elements_nav.split('>')
                product_information['Tipo']=nav_segment[-1]
                
        descripcion_corta_item=product_container.find('h1',itemprop="name")
        if descripcion_corta_item:
            product_information['DescripcionCorta']=descripcion_corta_item.text.strip()

        descripcion_larga_item=product_container.find(class_="product-details-wrapper")
        if descripcion_larga_item:
            descripcion_lines=descripcion_larga_item.text.splitlines()
            descripcion_='. '.join(descripcion_lines)
            default_loc=descripcion_.find('Default')
            product_information['DescripcionLarga']=descripcion_[:default_loc].strip()
            
            origen_item=product_information['DescripcionLarga'].find('Origen:')
            origen_fin=product_information['DescripcionLarga'].find('.',origen_item)
            if origen_item !=-1:
                product_information['PaisOrigen']=product_information['DescripcionLarga'][origen_item+8:origen_fin]

            variedad_item=product_information['DescripcionLarga'].find('Variedad:')
            variedad_fin=product_information['DescripcionLarga'].find('.',variedad_item)
            if variedad_item!=-1:
                product_information['Uva']=product_information['DescripcionLarga'][variedad_item+9:variedad_fin]
                
        marca_item=product_container.find(class_="grid product-meta-header")
        if marca_item:
            product_information['Marca']=marca_item.text.strip()
            
        precio_item=product_container.find(id="ProductPrice")
        if precio_item:
            product_information['Precio']=precio_item.text.strip()

        
        
        patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
        coincidencia = re.search(patron, product_information['DescripcionCorta'].lower())
        if coincidencia:
        # Si se encontró una coincidencia, obtenemos el resultado completo
            resultado = coincidencia.group(1)
            product_information['Tamaño']=resultado

        imagen_item=product_container.find(class_="product-medias__media")
        if imagen_item:
            imagen_src=imagen_item.find('img')
            product_information['Img']='https:'+imagen_src.get('src')


        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    else:
        return None
   

def pass_function():
    boton_sucursal = driver.find_element(By.ID, "sucursal_refresh")
    boton_sucursal.click()

    region_selector=Select(driver.find_element(By.ID,"region"))
    region_options=region_selector.options
    
    for region_option in region_options:
        region_option_value=region_option.get_attribute('value')
        region_selector.select_by_value(region_option_value)
        selected_region_option_text = region_selector.first_selected_option.text
        print(f"{region_option_value} - {selected_region_option_text}")

        sucursal_selector=Select(driver.find_element(By.ID,"sucursal"))
        sucursal_options=sucursal_selector.options
        
        for sucursal_option in sucursal_options:
            sucursal_option_value=sucursal_option.get_attribute('value')
            sucursal_selector.select_by_value(sucursal_option_value)
            selected_sucursal_option_text=sucursal_selector.first_selected_option.text
            print(f"{sucursal_option_value} - {selected_sucursal_option_text}")

    boton_entrar=driver.find_element(By.ID,"modal_sucursal_btn")
    boton_entrar.click()

def pagination(driver,link):
    URL = 'https://lcgroup.com.pe'
    print('pagination start')
    driver.get(link)
    # time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="boost-pfs-filter-bottom-pagination boost-pfs-filter-bottom-pagination-default")

    if main_body:
        pagination_html=main_body.find('ul')
        if pagination_html:
            pages_elements=pagination_html.find_all('li')
            pages_urls=pages_elements[-2].find('a')
            last_page=pages_urls.get('href').split('=')[-1]
            for i in range(1,int(last_page)+1):
                page_link=link+f'?page={i}'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver,fecha):
    INFORMANTE = 'LCGroup'
    URL = 'https://lcgroup.com.pe'
    
    informacion=[]
    
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="AccessibleNav")
    menu_items=menu.find_all('li',class_="site-nav--has-dropdown mega-menu")
    
    counter=0
    total_pages=0
    
    for item in menu_items:
        category_element=item.find('a')
        categoria=category_element.text.strip()
        tipo_element_menu=item.find('ul')
        tipo_elements=tipo_element_menu.find('li')
        sub_categories=tipo_elements.find_all('li')
        print(categoria)
        for sub_category in sub_categories:
            tipo_link=sub_category.find('a')
            link=URL+tipo_link.get('href')
            print(link)
            time.sleep(3)
            pages=pagination(driver,link)

            for page in pages:
                print(page)
                time.sleep(2)
                driver.get(page)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                body_products=soup.find(class_="boost-pfs-filter-right-col")
                if body_products:
                    products=body_products.find_all(class_="boost-pfs-filter-product-item-inner")
                    for product in products:
                        product_link_container=product.find('a')
                        product_link=URL+product_link_container.get('href')
                        print(product_link)
                        driver.get(product_link)
                        time.sleep(2)
                        
                        producto=agregar_informacion(BeautifulSoup(driver.page_source, 'html.parser'),
                    INFORMANTE,categoria,fecha)
                        if producto:
                            counter+=1
                            informacion.append(producto)
                            print(counter)
                        
                else:
                    producto=agregar_informacion(BeautifulSoup(driver.page_source, 'html.parser'),
                    INFORMANTE,categoria,fecha)
                    
                    if producto:
                        counter+=1
                        informacion.append(producto)
                        print(counter)
                
    return informacion
                                        

if __name__=='__main__':
    inicio = time.time()

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

    today = datetime.datetime.now()
    stamped_today = today.strftime("%Y-%m-%d")

    datos=productos_vinos(driver,stamped_today)
    filename='lcgroup_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    # link='https://lcgroup.com.pe/collections/tinto'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

