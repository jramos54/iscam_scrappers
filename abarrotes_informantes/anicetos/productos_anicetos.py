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
    
    
def login_page(driver):
    URL='https://dunosusapromociones.com/pickup/sesion'
    username='jrmsmolina54@gmail.com'
    password='arioto02'
        
    driver.get(URL)
    print('haciendo login')
    driver.find_element(By.ID,'usuario_login').send_keys(username)
    driver.find_element(By.ID,'password_login').send_keys(password)
    driver.find_element(By.ID,'begin').click()
    time.sleep(1)
    print('Seleccionando Tienda')
    ciudad_button = driver.find_element(By.ID,'ciudad_2378')
    ciudad_button.click()
    time.sleep(1)
    tienda_button=driver.find_element(By.ID,'tienda_13')
    tienda_button.click()
    time.sleep(1)
    
  
def sucursal_page(driver):
    URL_base='https://dunosusapromociones.com/pickup/'
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    page_categories=soup.find_all(id='addrow')
    categories=[]
    print('Extrayendo links de categorias')
    for page in page_categories:
        categories_links=page.find_all('a')
        for link_category in categories_links:
            link=URL_base+link_category.get('href')
            # print(link)
            categories.append(link)  
    time.sleep(5)
    return categories  


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


def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto


def tamano_producto(cadena):
    match = re.search(r'\d+\s*[A-Za-z]+', cadena)
    
    if match:
        return match.group()
    else:
        return ''


def sucursales_abarrotes(driver,fecha):

    caracteres_eliminar = ['-', '"']

    INFORMANTE='Los Anicetos'
    URL='https://losanicetos.mx/contacto/'
    driver.get(URL)
    time.sleep(5)
    
    radio_buttons = driver.find_elements(By.CLASS_NAME, "jet-radio-list__input")
    directorio=[]
    
    for radio_button in radio_buttons:
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
        print('click')
        driver.execute_script("arguments[0].click();", radio_button)
        
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        main=soup.find(id="content")
    
        sucursal_texto=main.find('div', {'data-id': 'fd78bf4'})
        if sucursal_texto:
            sucursal=sucursal_texto.text
            tienda['Sucursal']=sucursal.strip()

        direccion_texto=main.find('div',{'data-id':"585fa0b"})
        if direccion_texto:
            direccion=direccion_texto.text
            tienda['Direccion']=direccion.strip()

            tienda['CP']=obtencion_cp(tienda['Direccion'])
            
            longitud,latitud = geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud

        telefono_texto=main.find('div',{"data-id":"59072d8"})
        if telefono_texto:
            telefono=telefono_texto.text
            tienda['Telefono']=telefono.strip()
        
        print(json.dumps(tienda,indent=4))    
        directorio.append(tienda)

    return directorio


def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://losanicetos.mx/productos/'
    product_information = {
        'Informante': informante,
        'SKU':'',
        'Categoria':categoria,
        'DescripcionCorta':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Marca':'',
        'Img':'',
        'Fecha':fecha
        }
    
    texto_item=soup.text.strip()
    lines_texto=texto_item.splitlines()
    filtered_list = [item for item in lines_texto if item.strip()]

    # DESCRIPCION CORTA
    product_information['DescripcionLarga']=' '.join(filtered_list[:-1]).strip()
    product_information['DescripcionCorta']=' '.join(filtered_list[:2]).strip()
    # MARCA
    
    product_information['Marca']=filtered_list[0].strip()
  
    # SKU
    sku_text=filtered_list[2]
    sku_loc=sku_text.find(':')
    product_information['SKU']=sku_text[sku_loc+1:].strip()
    # time.sleep(1)

    size_text=filtered_list[1]
    size_partition=size_text.split('/')
    product_information['Tamaño'] = size_partition[-1].strip()
    
    # IMAGEN

    imagen=soup.find('img',class_="jet-carousel__item-img")
    if imagen:
        if imagen.get('src') != '':
            imagen_link=imagen.get('src')
            
            product_information['Img']=imagen_link
            
    # time.sleep(1)
    
    json_prod=json.dumps(product_information,indent=4)
    print(json_prod)

    return product_information


def pagination(driver,link):
    URL = 'https://dunosusapromociones.com/pickup/'
    print('iniciando paginacion')
    driver.get(link)
    time.sleep(2)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="shop-inner")
    print('Se accesa al link')
    if main_body:
        
        pagination_html=main_body.find(class_="pagination-area")
        list_url=pagination_html.find('ul')  
        print(bool(list_url))
        if list_url:
            print(bool(main_body))
            pages_urls=pagination_html.find_all('a')
            for page in pages_urls:
                link_page=URL+page.get('href')
                # print(link_page)
                pages.append(link_page)
        else:
            pages.append(link)
    else:
        pages.append(link)
    print(link)
    print(pages)
    time.sleep(3)
    return pages

def element_exists(by, value):
    try:
        driver.find_element(by, value)
        return True
    except NoSuchElementException:
        return False

def productos_abarrotes(driver, fecha):
    INFORMANTE = 'Los Anicetos'
    URL = ''
    BASE_URL='https://losanicetos.mx/productos/'
    informacion = []
    counter=0
    
    driver.get(BASE_URL)
    select_category = driver.find_element(By.CSS_SELECTOR,'select.jet-select__control[name="categoria"]')
    categories_selector=Select(select_category)
    
    for option in categories_selector.options:
        category=option.text.strip()
        if category == 'Seleccionar':
            continue
        print(category)
        categories_selector.select_by_value(option.get_attribute("value"))
        time.sleep(10)
        if element_exists(By.CLASS_NAME, 'jet-filters-pagination'):
            print('pagination starts')
            while True:
                # pagination_element = driver.find_element(By.CLASS_NAME, 'jet-filters-pagination')
                time.sleep(5)
                html=driver.page_source
                soup=BeautifulSoup(html,'html.parser')
                product_items = soup.find_all(class_="elementor elementor-248")
                for product in product_items:
                    dato=agregar_informacion(product,INFORMANTE,category,fecha)
                    informacion.append(dato)
                    counter+=1
                    print(counter)
                current_page=soup.find(class_="jet-filters-pagination__item jet-filters-pagination__current")
                print(f"on page {current_page.text}")
                if element_exists(By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']"):
                    element=driver.find_element(By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']")
                    x_offset=element.location['x']
                    y_offset=element.location['y']
                    print(element.location)
                    
                    wait = WebDriverWait(driver, 10)
                    element = driver.find_element(By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']")
                    driver.execute_script("arguments[0].click();", element)
                    
                    # next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='jet-filters-pagination__item prev-next next']/div[@class='jet-filters-pagination__link']")))

                    # next_button.click()
                    # actions = ActionChains(driver)
                    # actions.move_to_element(element).move_by_offset(x_offset, y_offset).click().perform()

                    driver.implicitly_wait(30)
                else:
                    break
        else:
            print('pagination doesnt exist')
            time.sleep(5)
            html=driver.page_source
            soup=BeautifulSoup(html,'html.parser')
            product_items = soup.find_all(class_="elementor elementor-248")
            
            for product in product_items:
                dato=agregar_informacion(product,INFORMANTE,category,fecha)
                informacion.append(dato)
                counter+=1
                print(counter)
            
        print('='*50)
    
            
    return informacion           
                

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
    # login_page(driver)
    # categories_pages=sucursal_page(driver)
    datos=productos_abarrotes(driver,stamped_today)
    filename='anicetos_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    sucursal_datos=sucursales_abarrotes(driver,stamped_today)
    filename='anicetos_tiendas_'+stamped_today+'.csv'
    exportar_csv(sucursal_datos,filename)
    driver.quit()

    print(f"{time.time()-inicio}")

# logout_link = driver.find_element(By.XPATH,'//div[@class="log out"]/a')
#     logout_link.click()