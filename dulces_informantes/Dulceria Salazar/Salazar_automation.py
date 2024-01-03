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

def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https://www.dulceriasalazar.com/pages/categorias'
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'TamañoMayoreo':'',
        'Img':'',
        'Fecha':fecha
        }
    container=soup.find(id="main")
    if container:
        # SKU
        # sku=container.find('span',class_="sku")
        # if sku:
        #     sku_text=sku.text
        #     product_information['SKU']=sku_text.strip()
        time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find(class_="product-meta__title")
        if descripcion_corta:
            caracteres_eliminar = ['-', '"', '.']
            descripcion_text=descripcion_corta.text.strip()

            product_information['DescripcionCorta']=limpiar_texto(descripcion_text,caracteres_eliminar)
            
            desc_corta_list=product_information['DescripcionCorta'].split()
            if len(desc_corta_list)>1:
                if len(desc_corta_list[-2])>3:
                    size=tamano_producto(desc_corta_list[-2])
                    product_information['Tamaño']=size.strip('\n')
                else:
                    size=tamano_producto(''.join(desc_corta_list[-3:-1]))
                    product_information['Tamaño']=size.strip('\n')

            
            #  # MARCA
            # marca_text=product_information['DescripcionCorta'].split()
            # product_information['Marca']=marca_text[0]
        time.sleep(2)
        
        # PRECIO
        precio=container.find(class_="price")
        if precio:
            precio_text=precio.text.strip()
            symbol_loc=precio_text.find('$')
            product_information['Precio']=precio_text[symbol_loc:]
        time.sleep(2)

        # DESCRIPCION LARGA
        descripcion_larga=container.find(class_="rte text--pull")
        
        if descripcion_larga:
            lines=descripcion_larga.text.splitlines()
            for line in lines:
                if 'caja' in line:
                    caja_loc=line.lower().find('caja')
                    size=tamano_producto(line[caja_loc:])
                    product_information['TamañoMayoreo']=size.strip()
            product_information['DescripcionLarga']=' '.join(lines).strip()
 
        # IMAGEN
        imagen_container=container.find(class_="product-gallery product-gallery--with-thumbnails")
        if imagen_container:
            imagen=imagen_container.find('img',class_="product-gallery__image image--fade-in lazyautosizes lazyloaded")
            if imagen:
                if imagen.get('data-zoom') != '':
                    imagen_link=imagen.get('data-zoom')
                    
                    product_information['Img']='https:'+imagen_link
                
        time.sleep(2)

        print(f"###> {informante} --> {categoria} ###> ")
        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link,informante):
    URL = ''
    
    print(f"###> Paginacion # {informante} # --> {link}")
    
    driver.get(link)
    time.sleep(2)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find(id="main")

    if main_body:
        pagination_html=main_body.find(class_="pagination__nav")
            
        if pagination_html:
            pages_urls=pagination_html.find_all('a')
            last_page=pages_urls[-1].get('href').split('=')[-1]
            for i in range(1,int(last_page)+1):
                page_link=link+f'?page={i}'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return pages


def productos_dulces(driver, fecha):
    INFORMANTE = 'Dulceria Salazar'
    URL = 'https://www.dulceriasalazar.com/pages/categorias'
    BASE_URL='https://www.dulceriasalazar.com'
    informacion = []

    print(f"###> Scrapping de # {INFORMANTE} ## {URL} #")
    
    driver.get(URL)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="main")
    containers=menu.find_all('div', class_="container")
    categories=[]
    for container in containers:
        cat_links=container.find_all('a')
        categories+=cat_links
      
    counter=0
    for category in categories:
       
        categoria=category.text.strip()
        link_categoria=BASE_URL+category.get('href')
        
        print(f'###> {INFORMANTE} --> {categoria}')
        print(f'###> {INFORMANTE} --> {link_categoria}')
        
        time.sleep(2)
        pages=pagination(driver,link_categoria,INFORMANTE)
        
        for page in pages:
            print(f'###> {INFORMANTE} --> {page}')

            driver.get(page)
            time.sleep(2)
            html_source=driver.page_source
            soup=BeautifulSoup(html_source,'html.parser')
        
            main_container=soup.find(id="main")

            main_list=main_container.find(class_="product-list product-list--collection product-list--with-sidebar")
            if main_list:
                products=main_list.find_all('div',recursive=False)

                for product in products:
                    link_product=product.find('a',class_="product-item__title text--strong link")
                    link=BASE_URL+link_product.get('href')
                    print(f"###> {INFORMANTE} Scrapping --> {link}")
                    driver.get(link)
                    time.sleep(2)
                    dato=agregar_informacion(BeautifulSoup(driver.page_source,'html.parser'),INFORMANTE,categoria,fecha)
                    informacion.append(dato)
                    counter+=1
                    print(f'###> {INFORMANTE} --> {counter}')
            
    return informacion           
           
                
def sucursales_dulces(driver,fecha):
    INFORMANTE='Dulceria Salazar'
    URL='https://www.dulceriasalazar.com/pages/sucursales'
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    main=soup.find(id="main")

    sucursales_tags=main.find_all('h1')
    sucursales=[h1 for h1 in sucursales_tags if h1.get_text(strip=True)]
    sucursales.pop(0)
  
    directorio=[]
    direcciones=main.find_all(class_="SALvLe")

    telefonos_tags=main.find_all(class_="LrzXr zdqRlf kno-fv")
    telefonos=[tel for tel in telefonos_tags if tel.get_text(strip=True)]

    compresed=zip(sucursales,direcciones,telefonos)
    

    for sucursal in compresed:
        
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

        sucursal_texto=sucursal[0].text
        tienda['Sucursal']=sucursal_texto

        direccion_texto=sucursal[1].text.strip()
        direccion_lineas=direccion_texto.splitlines()
        for linea in direccion_lineas:
            if 'Dirección' in linea:
                tienda['Direccion']=linea[11:]

        tienda['CP']=obtencion_cp(tienda['Direccion'])
        
        longitud,latitud = geolocalizacion(tienda['Direccion'])
        tienda['Latitud'] = latitud
        tienda['Longitud'] = longitud

        tienda['Telefono']=sucursal[-1].text.strip()
        directorio.append(tienda)

    return directorio


def main(driver,stamped_today):
    # Se toma el argumento del directorio destino
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()

    # Ejecucion normal del script
    datos=productos_dulces(driver,stamped_today)
    
    filename=args.ruta + 'salazar_productos_'+stamped_today+'.csv' 
    exportar_csv(datos,filename)


if __name__=='__main__':
    inicio=time.time()
    print(f"###> Se inicia la ejecucion de {__file__}")
    
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

    # Se debe ejecutar en la funcion main, para que tome como argumento el directorio destino del csv
    
    main(driver,stamped_today)
    
    # sucursal_datos=sucursales_dulces(driver,stamped_today)
    # filename='salazar_tiendas_'+stamped_today+'.csv'
    # exportar_csv(sucursal_datos,filename)

    driver.quit()

    print(f"{time.time()-inicio}")

