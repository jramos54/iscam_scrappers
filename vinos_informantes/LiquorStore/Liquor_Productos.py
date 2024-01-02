import os,datetime,json,time,requests,re,csv


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def text_segments(texto,word):
    segmentos_encontrados = []
    text=texto.lower()
    inicio = 0
    alc_pos = text.find(word, inicio)

    while alc_pos != -1:
        siguiente_alc_pos = text.find(word, alc_pos + 1)

        if siguiente_alc_pos == -1:
            segmento = text[alc_pos:]
        else:
            segmento = text[alc_pos:siguiente_alc_pos]

        segmentos_encontrados.append(segmento.strip())
        inicio = alc_pos + 1
        alc_pos = text.find(word, inicio)

    return segmentos_encontrados

def agregar_informacion(soup,informante,fecha):
    URL = 'https://elliquorstore.com'
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
    container=soup.find(id="page-wrapper")
    if container:
        # SKU
        sku=container.find('div',class_="product-meta-item product-sku")
        if sku:
            sku_text=sku.find('div',class_="field-item").text
            product_information['SKU']=sku_text.strip('\n')
        time.sleep(1)

        # DESCRIPCION CORTA
        descripcion_corta=container.find('div',class_="product-title")
        if descripcion_corta:
            product_information['DescripcionCorta']=descripcion_corta.text.strip()
        time.sleep(1)

        # TIPO
        tipo_producto=container.find('div',class_="product-meta-item product-category")
        if tipo_producto:
            tipo_text=tipo_producto.find('a')
            if tipo_text:
                tipo=tipo_text.text.strip()
                product_information['Tipo']=tipo
                product_information['Categoria']=tipo
        time.sleep(1)


        # PRECIO
        precio=container.find('div',class_="product-price-wrap")
        if precio:
            product_information['Precio']=precio.text.strip()
        time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find('div',class_="product-tab-item")
        
        if descripcion_larga:

            descripcion_larga_text=descripcion_larga.find('p')
            if descripcion_larga_text:
                total_lines=descripcion_larga_text.text.strip().strip('\n').strip('\t')
                lines=total_lines.splitlines()
                # lines.pop(0)
                descripcion_larga_=' '.join(lines)
                product_information['DescripcionLarga']=descripcion_larga_.strip()
                time.sleep(1)

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
                time.sleep(1)


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
                time.sleep(1)

            
        # MARCA
        # PAIS ORIGEN
                pais_loc=total_lines.lower().find('pais')
                if pais_loc != -1:
                    pais_end=total_lines.find(' ',pais_loc+6)
                    texto_pais=total_lines[pais_loc+6:pais_end].strip()
                    lineas_pais=texto_pais.splitlines()
                    product_information['PaisOrigen']= lineas_pais[0]           
            # UVA
                uva_loc=total_lines.lower().find('uva')
                if uva_loc != -1:
                    uva_end=total_lines.find(' ',uva_loc+5)
                    texto_uva=total_lines[uva_loc+4:uva_end].strip()
                    lineas_uva=texto_uva.splitlines()
                    product_information['Uva']=lineas_uva[0]
                time.sleep(1)

        # TAMANO
                print('tamano')
                patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
                coincidencia = re.search(patron, product_information['DescripcionCorta'].lower()+'\n'+total_lines.lower())
                if coincidencia:
                # Si se encontró una coincidencia, obtenemos el resultado completo
                    resultado = coincidencia.group(1)
                    product_information['Tamaño']=resultado

                time.sleep(1)
            else:
                product_information['DescripcionLarga']=product_information['DescripcionCorta']
                # TAMANO
                patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
                coincidencia = re.search(patron, product_information['DescripcionCorta'].lower())
                if coincidencia:
                # Si se encontró una coincidencia, obtenemos el resultado completo
                    resultado = coincidencia.group(1)
                    product_information['Tamaño']=resultado

                time.sleep(1)

        # MARCA
        marca=container.find('div',class_="product-meta-item product-brand")
        if marca:
            marca_text=marca.find('div',class_="field-item")
            if marca_text:
                product_information['Marca']=marca_text.text.strip()

        # IMAGEN
        imagen_container=container.find('div',class_="piczoomer")
        imagen=imagen_container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link=URL+imagen.get('src')
                product_information['Img']=imagen_link
        time.sleep(1)

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

    main_body=soup.find(id="page-wrapper")

    if main_body:
        pagination_html=main_body.find('nav',class_="pager").find_all('li')
            
        if pagination_html:
            pages_urls=pagination_html[-1].find('a')
            last_page=pages_urls.get('href').split('=')[-1]
            for i in range(0,int(last_page)+1):
                page_link=link+f'?sort_by=created&page={i}'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return tuple(pages)


def exportar_csv(diccionarios, nombre_archivo):
    encabezados = diccionarios[0].keys()

    with open(nombre_archivo, 'w', newline='',encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados, delimiter='|')

        writer.writeheader()
        for diccionario in diccionarios:
            writer.writerow(diccionario)
            

def productos_vinos(driver, fecha):
    INFORMANTE = 'Liquor Store'
    URL = 'https://elliquorstore.com/productos'
    base_url='https://elliquorstore.com'
    informacion = []

    pages=pagination(driver,URL)

    counter=0
    total_pages=0
    
    for page in pages:
        print(page)
        driver.get(page)
        time.sleep(3)
        page_html=BeautifulSoup(driver.page_source,'html.parser')
        main_body=page_html.find(id="page-wrapper")

        product_section=main_body.find('div',class_="row grid-wrapper")
        products=product_section.find_all('div',recursive=False)
        for product in products:
            product_link=base_url+product.find('a').get('href')
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

    datos=productos_vinos(driver,stamped_today)
    filename='Liquorstore_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)
    
    driver.quit()

    print(f"{time.time()-inicio}")

