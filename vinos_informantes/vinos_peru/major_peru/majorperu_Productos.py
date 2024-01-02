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
    URL = 'https:'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'SKU':'',
        'DescripcionCorta':'',
        'Tipo':categoria,
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
    container=soup.find(class_="et-l et-l--body")
    if container:
        # SKU
        # sku=container.find('meta',itemprop="sku")
        # if sku:
        #     sku_float=float(sku.get('content'))
        #     sku_str=str(sku_float)
        #     product_information['SKU']=sku_str[:4]

        # DESCRIPCION CORTA
        descripcion_corta=container.find('h1')
        if descripcion_corta:
            descripcion_corta_=descripcion_corta.text
            product_information['DescripcionCorta']=descripcion_corta_.strip()
        time.sleep(1)

        # # TIPO
        #     if product_information['DescripcionCorta'].startswith('Vino'):

        #         tipo_producto=product_information['DescripcionCorta'].split()
        #         product_information['Tipo']=tipo_producto[0]+' '+tipo_producto[1]
        #     else:
        #         tipo_producto=product_information['DescripcionCorta'].split()
        #         product_information['Tipo']=tipo_producto[0]
            # time.sleep(1)


        # PRECIO
        precio=container.find('p',class_="price")
        if precio:
            precio_text=precio.text.strip()
            # precio_loc=precio_text.find('$')
            # if precio_loc != -1:
            product_information['Precio']=precio_text
        time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="et_pb_row_inner et_pb_row_inner_3_tb_body")
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
            # recomendacion_loc=total_lines.find('GASTRONOMÍA')
            # if maridaje_loc != -1:
            #     maridaje_end=total_lines[maridaje_loc+10:].find('\n')
            #     if maridaje_end == -1:
            #         maridaje_text=total_lines[maridaje_loc+10:]
            #     else:
            #         maridaje_text=total_lines[maridaje_loc+10:maridaje_loc+10+maridaje_end]
            # elif recomendacion_loc != -1:
            #     recomendacion_end=total_lines[recomendacion_loc+12:].find('.')
            #     maridaje_text=total_lines[recomendacion_loc+11:recomendacion_loc+recomendacion_end+11]
            #     maridaje_text_lines=maridaje_text.splitlines()
            #     maridaje_text=' '.join(maridaje_text_lines)
            # product_information['Maridaje']=maridaje_text
            # time.sleep(1)


        #   time.sleep(1)
            
        # ALCVOL
            # alcvol=''
            # alc_seg=text_segments(descripcion_larga_.lower(),'alc')
            # for seg in alc_seg:
            #     if '%' in seg:
            #         seg_loc=seg.find(' ')
            #         seg_end=seg.find('%')
            #         alcvol=seg[seg_loc+1:seg_end+1]
            # if len(alcvol)>8:
            #     loc_alc=total_lines.find('alc')
            #     alcvol=total_lines[loc_alc-5:loc_alc].strip()
            #     product_information['AlcVol']=alcvol.strip('\n')
            # else:
            #     product_information['AlcVol']=alcvol.strip('\n')
            # time.sleep(1)

            
        # MARCA
        information_table=container.find('table',class_="woocommerce-product-attributes shop_attributes")
        # PAIS ORIGEN
        if information_table:
            information_rows=information_table.find_all('tr')     
            
            for row in information_rows:
                row_header=row.find('th').text.strip()
                if row_header == 'Marca':
                    product_information['Marca']=row.find('td').text.strip()
                elif row_header == 'País':
                    product_information['PaisOrigen']= row.find('td').text.strip()
            # UVA
                elif row_header == 'Cepa':
                    product_information['Uva']=row.find('td').text.strip()
                # time.sleep(1)
                elif row_header == 'Volumen':
                    product_information['Tamaño']=row.find('td').text.strip()

           
        # IMAGEN
        imagen_container=container.find(class_="woocommerce-product-gallery__wrapper")
        imagen=imagen_container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link=imagen.get('src')
                product_information['Img']=imagen_link
        # time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = 'https://majorperu.com/'
    
    driver.get(link)
    time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(class_="woocommerce-pagination")
    if main_body:
        pagination_html=main_body.find_all('li')
                
        if pagination_html:
            
            last_page=pagination_html[-2].text
            for i in range(1,int(last_page)+1):
                page_link=link+f'page/{i}/'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver, fecha):
    INFORMANTE = 'Major Peru'
    URL = 'https://majorperu.com/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(class_="et_pb_section et_pb_section_2_tb_header et_section_regular")
    itemslevel0=menu.find_all(class_="et_pb_blurb_container")
    
    counter=0
    total_pages=0

    for itemlevel0 in itemslevel0[0:4]:
        title=itemlevel0.find('h4').text
        url_item=itemlevel0.find('a').get('href')
        # print(title)
        print('='*50)
        print(url_item)
        
        driver.get(url_item)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        if title == 'Cerveza':
            categoria=title
            print(categoria)
            pages=pagination(driver,link)
            result=product_scrapping(driver,pages,INFORMANTE,categoria,fecha)
            informacion.extend(result)
            
        else:
            sub_menu_container= soup.find(class_="entry-content")
            if sub_menu_container:
                
                cat_container=sub_menu_container.find(class_="et_pb_section et_pb_section_0 et_section_regular")
                sub_cat_container=cat_container.find(class_="et_pb_column et_pb_column_1_4 et_pb_column_0 et_pb_css_mix_blend_mode_passthrough")
                if sub_cat_container:
                    sub_categories=sub_cat_container.find_all('a')
                    for category in sub_categories:
                        categoria=category.parent.parent.text.strip()
                        link=category.get('href')
                        print(categoria)
                        print(link)
                        pages=pagination(driver,link)
                        result=product_scrapping(driver,pages,INFORMANTE,categoria,fecha)
                        informacion.extend(result)
    return informacion
                    
def product_scrapping(driver,pages,INFORMANTE,categoria,fecha):
    informacion=[]
    
    for page in pages:
        driver.get(page)
        time.sleep(5)
        page_html=BeautifulSoup(driver.page_source,'html.parser')
        
        main_body=page_html.find(class_="entry-content")
        product_section=main_body.find(class_="et_pb_section et_pb_section_0 et_section_regular")
        sub_section=product_section.find(class_="et_pb_column et_pb_column_3_4 et_pb_column_1  et_pb_css_mix_blend_mode_passthrough et-last-child")
        products=product_section.find_all('li')
        
        for product in products:
            
            product_url=product.find('a')
            if product_url:
                product_link=product_url.get('href')
                
                time.sleep(2)
                driver.get(product_link)

                producto=agregar_informacion(
                    BeautifulSoup(driver.page_source, 'html.parser'),INFORMANTE,categoria,fecha)
                
                if producto:
                    informacion.append(producto)
                    
    return informacion            


def no_duplicates(archivo_entrada):
    archivo_salida = archivo_entrada[:-4]+'_noduplicates.csv'
    lineas_unicas = []
    lineas_vistas = set()

    with open(archivo_entrada, 'r', newline='',encoding='utf-8') as csvfile:
        lector_csv = csv.DictReader(csvfile, delimiter='|')
        encabezados = lector_csv.fieldnames

        lineas_unicas.append(encabezados)  # Agrega los encabezados al archivo de salida

        for fila in lector_csv:
            descripcion_corta = fila['DescripcionCorta']
            if descripcion_corta not in lineas_vistas:
                lineas_unicas.append([fila[campo] for campo in encabezados])
                lineas_vistas.add(descripcion_corta)

    # Escribe las líneas únicas en un nuevo archivo CSV
    with open(archivo_salida, 'w', newline='',encoding='utf-8') as csvfile:
        escritor_csv = csv.writer(csvfile, delimiter='|')
        escritor_csv.writerows(lineas_unicas)


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

    datos = productos_vinos(driver, stamped_today)
    filename = f'majorperu_productos_{stamped_today}.csv'
    exportar_csv(datos, filename)
    no_duplicates(filename)

    
    # link='https://majorperu.com/vino-tinto/'
    # pages=pagination(driver,link)
    # for page in pages:
    #     print(page)
    #     response=requests.get(page)
    #     print(response.status_code)
    # driver.quit()

    print(f"Tiempo de ejecución: {time.time() - inicio} segundos")

    
