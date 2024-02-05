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
    container=soup.find('article')
    if container:
        # SKU
        # sku=container.find('meta',itemprop="sku")
        # if sku:
        #     sku_float=float(sku.get('content'))
        #     sku_str=str(sku_float)
        #     product_information['SKU']=sku_str[:4]

        # DESCRIPCION CORTA
        descripcion_corta=container.find('h1',{"data-hook":"product-title"})
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text.strip()
        time.sleep(1)

        # TIPO
        # tipo_producto=container.find('p',class_="productInfo--collection")
        # if tipo_producto:
        #     tipo_text=tipo_producto.text.split()
        #     tipo=tipo_text[-1]
        #     product_information['Tipo']=tipo
        # time.sleep(1)


        # PRECIO
        precio=container.find('span',{"data-hook":"formatted-primary-price"})
        if precio:
            precio_text=precio.text.strip()
            product_information['Precio']=precio_text
        time.sleep(1)

        # DESCRIPCION LARGA
        # descripcion_larga=container.find('div',class_="smart-tabs-wrapper Rte")
        # if descripcion_larga:

        #     total_lines=descripcion_larga.text.strip().strip('\n').strip('\t')
        #     total_lines=total_lines[:-10]
        #     lines=total_lines.splitlines()
        #     # lines.pop(0)
        #     descripcion_larga_='. '.join(lines)
        #     desc_loc=descripcion_larga_.find('FICHA')
        #     descripcion_larga_=descripcion_larga_[desc_loc+14:]
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
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
        coincidencia = re.search(patron, product_information['DescripcionCorta'].lower())
        if coincidencia:
# Si se encontró una coincidencia, obtenemos el resultado completo
            resultado = coincidencia.group(1)
            product_information['Tamaño']=resultado

        time.sleep(1)

        # IMAGEN
        
        imagen=container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link=imagen.get('src')
                product_information['Img']=imagen_link
        time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = 'https://www.vinicolasantabarbaraonline.com/'
    
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
    INFORMANTE = 'Vinicola Santa Barbara'
    URL = 'https://www.vinicolasantabarbaraonline.com/wines'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="PAGES_CONTAINER")
    menu_level0=menu.find('li',{"data-hook":"filter-type-COLLECTION"})
    itemslevel0= menu_level0.find_all('li')
    
    counter=0
    total_pages=0

    for itemlevel0 in itemslevel0[1:]:
        
        categoria=itemlevel0.text.strip()
        list_categoria=categoria.split()
        if len(list_categoria)>1:
            link=URL+'?Categoría='+'+'.join(list_categoria)
        else:
            link=URL+'?Categoría='+categoria
        print(categoria)
        
        time.sleep(5)

        driver.get(link)
        page_html=BeautifulSoup(driver.page_source,'html.parser')
        pagination_initial=page_html.find('button',{"data-hook":"load-more-button"})

        pages=[]
        more_pages=True
        if pagination_initial:
            pagina=1
            while more_pages:
                new_link=link+'&page='+f"{pagina}"
                pages.append(new_link)
                driver.get(new_link)
                time.sleep(5)
                page_html=BeautifulSoup(driver.page_source,'html.parser')
                pagination_pages=page_html.find('button',{"data-hook":"load-more-button"})
                if pagination_pages:
                    pagina+=1
                else:
                    more_pages=False

        else:
            pages.append(link)

        for page in pages:
    
            driver.get(page)
            time.sleep(2)
            page_html=BeautifulSoup(driver.page_source,'html.parser')
            main_body=page_html.find('section',{"data-hook":"product-list"})

            product_section=main_body.find('ul')
            products=product_section.find_all('li',recursive=False)
            for product in products:
                product_link=product.find('a').get('href')
                
                time.sleep(2)
                driver.get(product_link)

                producto=agregar_informacion(
                    BeautifulSoup(driver.page_source, 'html.parser'),
                    INFORMANTE,categoria,fecha)
                
                if producto:
                    informacion.append(producto)
                    counter+=1
                    print(counter)
    
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
    chrome_options.add_argument('--js-flags=--max-old-space-size=4096')
    
    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    datos=productos_vinos(driver,stamped_today)
    filename='vinicola_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)

    driver.quit()

    print(f"{time.time()-inicio}")

