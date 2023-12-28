import os,datetime,json,time,requests,re,csv

# Importar Selenium webdriver
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


def exportar_csv(diccionarios, nombre_archivo):
    encabezados = diccionarios[0].keys()

    with open(nombre_archivo, 'w', newline='',encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados, delimiter='|')

        writer.writeheader()
        for diccionario in diccionarios:
            writer.writerow(diccionario)


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


def agregar_informacion(soup,informante,categoria,fecha):
    URL = 'https:'
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
    container=soup.find(id="ProductSection")
    if container:
        # SKU
        # sku=container.find('meta',itemprop="sku")
        # if sku:
        #     sku_float=float(sku.get('content'))
        #     sku_str=str(sku_float)
        #     product_information['SKU']=sku_str[:4]

        # DESCRIPCION CORTA
        descripcion_corta=container.find('h1',itemprop="name")
        if descripcion_corta:
            descripcion_corta_=descripcion_corta.text.split('/')
            product_information['DescripcionCorta']=descripcion_corta_[0]
            # time.sleep(1)

        # TIPO
            if product_information['DescripcionCorta'].startswith('Vino'):

                tipo_producto=product_information['DescripcionCorta'].split()
                product_information['Tipo']=tipo_producto[0]+' '+tipo_producto[1]
            else:
                tipo_producto=product_information['DescripcionCorta'].split()
                product_information['Tipo']=tipo_producto[0]
            # time.sleep(1)


        # PRECIO
        # precio=container.find('p',itemprop="offers")
        # if precio:
        #     precio_text=precio.text.strip()
        #     precio_loc=precio_text.find('$')
        #     if precio_loc != -1:
        #         product_information['Precio']=precio_text[precio_loc:]
        # time.sleep(1)

        # DESCRIPCION LARGA
        descripcion_larga=container.find('div',itemprop="description")
        if descripcion_larga:

            total_lines=descripcion_larga.text.strip().strip('\n').strip('\t')
            
            lines=total_lines.splitlines()
            # lines.pop(0)
            descripcion_larga_=' '.join(lines)
            product_information['DescripcionLarga']=descripcion_larga_.strip()
            # time.sleep(1)


        # MARIDAJE
            maridaje_text=''
            maridaje_loc=total_lines.find('Maridaje')
            recomendacion_loc=total_lines.find('GASTRONOMÍA')
            if maridaje_loc != -1:
                maridaje_end=total_lines[maridaje_loc+10:].find('\n')
                if maridaje_end == -1:
                    maridaje_text=total_lines[maridaje_loc+10:]
                else:
                    maridaje_text=total_lines[maridaje_loc+10:maridaje_loc+10+maridaje_end]
            elif recomendacion_loc != -1:
                recomendacion_end=total_lines[recomendacion_loc+12:].find('.')
                maridaje_text=total_lines[recomendacion_loc+11:recomendacion_loc+recomendacion_end+11]
                maridaje_text_lines=maridaje_text.splitlines()
                maridaje_text=' '.join(maridaje_text_lines)
            product_information['Maridaje']=maridaje_text
            # time.sleep(1)


        #   time.sleep(1)
            
        # ALCVOL
            alcvol=''
            alc_seg=text_segments(descripcion_larga_.lower(),'alc')
            for seg in alc_seg:
                if '%' in seg:
                    seg_loc=seg.find(' ')
                    seg_end=seg.find('%')
                    alcvol=seg[seg_loc+1:seg_end+1]
            if len(alcvol)>8:
                loc_alc=total_lines.find('alc')
                alcvol=total_lines[loc_alc-5:loc_alc].strip()
                product_information['AlcVol']=alcvol.strip('\n')
            else:
                product_information['AlcVol']=alcvol.strip('\n')
            # time.sleep(1)

            
        # MARCA
        # PAIS ORIGEN
             
            
            if len(descripcion_corta_)>1:
                product_information['PaisOrigen']=descripcion_corta_[-1].strip('\n').strip()
            else:
                pais_loc=total_lines.lower().find('país')
                if pais_loc != -1:
                    separator_loc=total_lines.find(':',pais_loc)
                    pais_end=total_lines.find(' ',separator_loc+2)
                    texto_pais=total_lines[separator_loc+1:pais_end].strip()
                    lineas_pais=texto_pais.splitlines()
                    if lineas_pais:
                        product_information['PaisOrigen']= lineas_pais[0].strip('\n').strip()
        # UVA
            # uva_loc=total_lines.lower().find('variedad')
            # if uva_loc != -1:
                
            #     des_begin=total_lines.find('\n',uva_loc+9)
            #     uva_end=total_lines.find('\n',des_begin+1)
            #     texto_uva=total_lines[des_begin+1:uva_end].strip()
            #     lineas_uva=texto_uva.splitlines()
            #     if lineas_uva:
            #         product_information['Uva']=lineas_uva[0]
            # time.sleep(1)

        # TAMANO
            patron=r'(\d+\s*ml)'
            coincidencia = re.search(patron, product_information['DescripcionCorta'].lower()+'\n'+total_lines.lower())
            if coincidencia:
    # Si se encontró una coincidencia, obtenemos el resultado completo
                resultado = coincidencia.group(1)
                product_information['Tamaño']=resultado

            # time.sleep(1)
        else:
            product_information['DescripcionLarga']=product_information['DescripcionCorta']

        # IMAGEN
        imagen_container=container.find('div',id="productPhoto")
        imagen=imagen_container.find('img')
        if imagen:
            if imagen.get('src') != '':
                imagen_link='https:'+imagen.get('src')
                product_information['Img']=imagen_link
        # time.sleep(1)

        json_prod=json.dumps(product_information,indent=4)
        print(json_prod)

        return product_information
    return None


def pagination(driver,link):
    URL = 'https://celca.myshopify.com/'
    
    driver.get(link)
    time.sleep(5)
    html=driver.page_source
    soup=BeautifulSoup(html,'html.parser')
    pages=[]

    main_body=soup.find('div',class_="grid-item pagination-border-top")
    if main_body:
        pagination_html=main_body.find_all('li')
                
        if pagination_html:
            pages_urls=pagination_html[-2].find('a')
            last_page=pages_urls.get('href').split('=')[-1]
            for i in range(1,int(last_page)+1):
                page_link=link+f'?page={i}'
                pages.append(page_link)
        else:
            pages.append(link)
    else:
        pages.append(link)

    return tuple(pages)


def productos_vinos(driver, fecha):
    INFORMANTE = 'Celca'
    URL = 'https://celca.myshopify.com/'
    informacion = []

    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="shopify-section-header")
    itemslevel0=menu.find_all('li',class_="site-nav--has-dropdown site-nav--active")
    
    counter=0
    total_pages=0

    for itemlevel0 in itemslevel0[:-1]:

        link_itemlevel0=itemlevel0.find('a')
        categoria=link_itemlevel0.text.strip()
        print(categoria)
        time.sleep(5)

        subcat=itemlevel0.find_all('li')

        for cat in subcat:
            link=URL+cat.find('a').get('href')
            pages=pagination(driver,link)
        # total_pages+=len(pages)
            for page in pages:
                driver.get(page)
                time.sleep(5)
                page_html=BeautifulSoup(driver.page_source,'html.parser')
                main_body=page_html.find('div',class_="grid grid-border")
                product_section=main_body.find('div',class_="grid-uniform")
                products=product_section.find_all('div',recursive=False)
                
                for product in products:
                    
                    product_url=product.find('a')
                    if product_url:
                        product_link=URL+product_url.get('href')
                        
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
    filename = f'celca_productos_{stamped_today}.csv'
    exportar_csv(datos, filename)

    driver.quit()

    print(f"Tiempo de ejecución: {time.time() - inicio} segundos")

    
