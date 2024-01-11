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
    URL = 'https://tienda.pangea-spirits.com'
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
    container=soup.find(id="product_detail")
    if container:
         # TIPO
        tipo_producto=container.find('div',class_="js_categ_div te_prod_bottom_margin")
        if tipo_producto:
            tipo_text=tipo_producto.find('a')
            tipo=tipo_text.text.strip()
            product_information['Tipo']=tipo
        time.sleep(1)

        # SKU
        sku=container.find('span',itemprop="url")
        if sku:
            split_sku=sku.text.split('/')
            sku_search=split_sku[-1].find(product_information['Tipo'].lower())
            product_information['SKU']=split_sku[-1][:sku_search-1].upper()
        time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find('h1',itemprop="name")
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text
        time.sleep(1)

        # PRECIO
        precio=container.find('b',class_="oe_price")
        if precio:
            precio_text=precio.text.strip()
            product_information['Precio']=precio_text
        time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=soup.find('div',itemprop="description")
        if descripcion_larga:

            total_lines=descripcion_larga.text.strip().strip('\n').strip('\t')
            lines=total_lines.splitlines()
            # lines.pop(0)
            descripcion_larga_=' '.join(lines)
            product_information['DescripcionLarga']=descripcion_larga_.strip()
            time.sleep(1)


        # MARIDAJE
            # maridaje_text=''
            # maridaje_loc=total_lines.find('Maridaje')
            # recomendacion_loc=total_lines.find('Se recomienda')
            # if maridaje_loc != -1:
            #     maridaje_end=total_lines[maridaje_loc+10:].find('\n')
            #     if maridaje_end == -1:
            #         maridaje_text=total_lines[maridaje_loc+10:]
            #     else:
            #         maridaje_text=total_lines[maridaje_loc+10:maridaje_loc+10+maridaje_end]
            # elif recomendacion_loc != -1:
            #     recomendacion_end=total_lines[recomendacion_loc:].find('.')
            #     maridaje_text=total_lines[recomendacion_loc:recomendacion_loc+recomendacion_end]
            # product_information['Maridaje']=maridaje_text
            # time.sleep(1)


        #   time.sleep(1)
            
        # ALCVOL
            # alcvol=''
            # alc_seg=text_segments(total_lines,'alc')
            # for seg in alc_seg:
            #     if '%' in seg:
            #         seg_loc=seg.find(' ')
            #         seg_end=seg.find('%')
            #         alcvol=seg[seg_loc+1:seg_end+1]
            # product_information['AlcVol']=alcvol
            # time.sleep(1)

            
        # MARCA
        # PAIS ORIGEN
            # pais_loc=total_lines.lower().find('pais')
            # if pais_loc != -1:
            #     pais_end=total_lines.find(' ',pais_loc+6)
            #     texto_pais=total_lines[pais_loc+6:pais_end].strip()
            #     lineas_pais=texto_pais.splitlines()
            #     product_information['PaisOrigen']= lineas_pais[0]           
        # UVA
            # uva_loc=total_lines.lower().find('uva')
            # if uva_loc != -1:
            #     uva_end=total_lines.find(' ',uva_loc+5)
            #     texto_uva=total_lines[uva_loc+4:uva_end].strip()
            #     lineas_uva=texto_uva.splitlines()
            #     product_information['Uva']=lineas_uva[0]
            # time.sleep(1)

        # TAMANO
            patron=r'(\d+\s*ml)'
            coincidencia = re.search(patron, product_information['DescripcionCorta'].lower()+'\n'+total_lines.lower())
            if coincidencia:
    # Si se encontró una coincidencia, obtenemos el resultado completo
                resultado = coincidencia.group(1)
                product_information['Tamaño']=resultado

            time.sleep(1)

        # IMAGEN
        imagen_container=container.find('div',id="o-carousel-product")
        imagen=imagen_container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link=imagen.get('src')
                product_information['Img']=URL+imagen_link
        time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = 'https://www.contrabarra.com.mx/'
    
    driver.get(link)
    # time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find('div',class_="pagination-wrapper sixteen columns")
    pagination_html=main_body.find_all('span',class_="page")
            
    if pagination_html:
        pages_urls=pagination_html[-1].find('a')
        last_page=pages_urls.get('href').split('=')[-1]
        for i in range(1,int(last_page)+1):
            page_link=link+f'?page={i}'
            pages.append(page_link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver, fecha):
    INFORMANTE = 'Pangea'
    URL = 'https://tienda.pangea-spirits.com/shop'
    BASE_URL='https://tienda.pangea-spirits.com'
    informacion = []

    driver.get(URL)
    # boton_entrar = driver.find_element(By.CLASS_NAME,"btn-close")
    # time.sleep(2)
    # boton_entrar.click()
    
    # time.sleep(2)
    # driver.save_screenshot("captura.png")
    time.sleep(3)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    main=soup.find('main')
    menu = main.find(class_="products_categories")
    itemslevel0=menu.find_all('li')
    counter=0
    total_pages=0
    

    for itemlevel0 in itemslevel0[1:]:
        print("ITERATING CATEGORIES...")
        
        link_itemlevel0=itemlevel0.find('div')
        link=link_itemlevel0['data-link-href']
        if not link_itemlevel0:
            continue
        categoria=link_itemlevel0.text.strip()
        print(categoria)
        link=BASE_URL+link
        driver.get(link)
        print(link)
        time.sleep(5)

        page_html=BeautifulSoup(driver.page_source,'html.parser')
        body_container=page_html.find('div',id="wrap")
        main_body=body_container.find(id="products_grid")

        product_section=main_body.find('table')
        if product_section:

            products=product_section.find_all('td',class_="oe_product te_shop_grid")
            
            for product in products:
                product_link=BASE_URL+product.find('a',itemprop="name").get('href')
                # print(product.find('a').text)
                print(product_link)
                time.sleep(2)
                driver.get(product_link)

                producto=agregar_informacion(
                    BeautifulSoup(driver.page_source, 'html.parser'),
                    INFORMANTE,categoria,fecha)
                
                if producto:
                    informacion.append(producto)
                    counter+=1
                    print(counter)
    print(total_pages)
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

    datos=productos_vinos(driver,stamped_today)
    filename='pangea_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    # link='https://www.contrabarra.com.mx/collections/vinos'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)

    driver.quit()

    print(f"{time.time()-inicio}")

