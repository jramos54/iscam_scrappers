import os,datetime,json,time,requests,re,csv,argparse

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

def agregar_informacion(soup,informante,fecha):
    URL = 'https://lamediterranea.mx/'
    product_information = {
        'Informante': informante,
        'Categoria':'',
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
    container=soup.find(id="content")
    if container:
        # SKU
        sku=container.find('span',class_="sku")
        if sku:
            sku_text=sku.text
            product_information['SKU']=sku_text.strip()
        # time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find('h1',class_="product_title entry-title")
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text.strip()
             # MARCA
            marca_text=product_information['DescripcionCorta'].split()
            product_information['Marca']=marca_text[0]
        # time.sleep(1)

        # TIPO
        category_container=container.find('nav',class_="woocommerce-breadcrumb")
        if category_container:
            category_list=category_container.find_all('a')
            categoria_text=category_list[1].get_text().strip()
            product_information['Categoria']=categoria_text

            data_container=container.find('span',class_="single-product-category")
            if data_container:
                data_text=data_container.text
                data_list=data_text.split(',')
                links_container=data_container.find_all('a')
                for link in links_container:
                    link_text=link.get('href')
                    if 'tipo/' in link_text and not link_text.endswith('tipo/'):
                        product_information['Tipo']=link.text.strip()
                    # if product_information['Categoria'].lower()=='vinos':

                    #     product_information['Tipo']=data_list[3].strip()
                    
                    # PAIS ORIGEN
                    if 'pais' in link_text and not link_text.endswith('pais/'):
                        product_information['PaisOrigen']=link.text.strip()
                        # product_information['PaisOrigen']= data_list[0]           
                    # UVA
                    if 'tipo-de-uva' in link_text and not link_text.endswith('tipo-de-uva/'):
                        if product_information['Uva']=='':
                            product_information['Uva']=link.text.strip()
                        else:
                            product_information['Uva']+=', '+link.text.strip()
                        
                    #     product_information['Uva']=data_list[2]
                    #     time.sleep(1)
                    # else:
                    #     product_information['Tipo']=data_list[-1].strip()
                    if 'categoria-producto' in link_text and product_information['Tipo'] == '':
                        product_information['Tipo']=link.text.strip()


        # PRECIO
        precio=container.find('p',class_="price")
        if precio:
            product_information['Precio']=precio.text.strip()
        # time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find('div',id="tab-description")
        
        if descripcion_larga:

            descripcion_larga_text=descripcion_larga.find('p')
            if descripcion_larga_text:
                total_lines=descripcion_larga_text.text.strip().strip('\n').strip('\t')
                lines=total_lines.splitlines()
                # lines.pop(0)
                descripcion_larga_=' '.join(lines)
                product_information['DescripcionLarga']=descripcion_larga_.strip()
                # time.sleep(1)

            # MARIDAJE
                maridaje_text=''
                maridaje_loc=total_lines.find('acompañar')
                if maridaje_loc != -1:
                    maridaje_end=total_lines[maridaje_loc:].find('\n')
                    if maridaje_end == -1:
                        maridaje_text=total_lines[maridaje_loc:]
                    else:
                        maridaje_text=total_lines[maridaje_loc:maridaje_loc+10+maridaje_end]
                product_information['Maridaje']=maridaje_text
                # time.sleep(1)


        #   time.sleep(1)
            
        # ALCVOL
                alcvol=''
                alc_seg=text_segments(total_lines,'alc')
                for seg in alc_seg:
                    if '%' in seg:
                        seg_loc=seg.find(' ')
                        seg_end=seg.find('%')
                        alcvol=seg[seg_loc+1:seg_end+1]
                if len(alcvol)>5:
                    loc_alc=total_lines.find('alc')
                    alcvol=total_lines[loc_alc-5:loc_alc].strip()
                    if '%' not in alcvol:
                        alcvol=''
                else:
                    product_information['AlcVol']=alcvol
                # time.sleep(1)

            
        # MARCA
        

        # TAMANO
                
                patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
                coincidencia = re.search(patron, product_information['DescripcionCorta'].lower()+'\n'+total_lines.lower())
                if coincidencia:
                # Si se encontró una coincidencia, obtenemos el resultado completo
                    resultado = coincidencia.group(1)
                    product_information['Tamaño']=resultado

                # time.sleep(1)
            else:
                product_information['DescripcionLarga']=product_information['DescripcionCorta']
                # TAMANO
                patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
                coincidencia = re.search(patron, product_information['DescripcionCorta'].lower())
                if coincidencia:
                # Si se encontró una coincidencia, obtenemos el resultado completo
                    resultado = coincidencia.group(1)
                    product_information['Tamaño']=resultado

                # time.sleep(1)

       

        # IMAGEN
        imagen_container=container.find('div',class_="woocommerce-product-gallery__wrapper")
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
    URL = ''
    
    driver.get(link)
    # time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find('nav',class_="woocommerce-pagination")

    if main_body:
        pagination_html=main_body.find('ul',class_="page-numbers").find_all('li')
            
        if pagination_html:
            pages_urls=pagination_html[-2].find('a')
            last_page=pages_urls.get('href').split('/')[-2]
            for i in range(1,int(last_page)+1):
                page_link=link+f'/page/{i}/'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver, fecha):
    INFORMANTE = 'La Mediterranea'
    URL = 'https://lamediterranea.mx/'
    categorias=['categoria-producto/vinos','categoria-producto/licores-y-destilados']
    informacion = []

    for categoria in categorias:
        url_cat=URL+categoria
        
        pages=pagination(driver,url_cat)

        counter=0
        total_pages=0
    
        for page in pages:
            print(page)
            driver.get(page)
            time.sleep(3)

            page_html=BeautifulSoup(driver.page_source,'html.parser')
            main_body=page_html.find(id="main")

            product_section=main_body.find('ul',class_="products columns-4")
            products=product_section.find_all('li',recursive=False)
            for product in products:
                product_link=product.find('a').get('href')
                # print(product.find('a').text)
                print(product_link)
                time.sleep(2)
                driver.get(product_link)

                producto=agregar_informacion(
                    BeautifulSoup(driver.page_source, 'html.parser'),
                    INFORMANTE,fecha)
                
                if producto:
                    informacion.append(producto)
                    counter+=1
                    print(counter)
    print(total_pages)
    return informacion            

def main(driver,stamped_today):
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()
                   
    datos=productos_vinos(driver,stamped_today)
    filename=args.ruta +'mediterranea_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
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

    main(driver,stamped_today)

    driver.quit()

    print(f"{time.time()-inicio}")

