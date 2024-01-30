import os,datetime,json,time,requests,re,csv,argparse


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
    URL = 'https://bp-peru.com/shop'
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
                      
            
    product_container=soup.find(id="main")
    if product_container:
        
        sku_item=product_container.find(class_="elementor-element elementor-element-cd40353 elementor-widget elementor-widget-text-editor")
        if sku_item:
            sku_text=sku_item.text.strip()
            sku=sku_text[4:]
            product_information['SKU']=sku.strip()
                        
        descripcion_corta_item=product_container.find('h1',class_="product_title entry-title")
        if descripcion_corta_item:
            product_information['DescripcionCorta']=descripcion_corta_item.text.strip()

        descripcion_larga_item=product_container.find({"data-widget_type":"text-editor.default"})
        if descripcion_larga_item:
            descripcion_lines=descripcion_larga_item.text.strip()
            product_information['DescripcionLarga']=descripcion_lines
            
        # marca_item=product_container.find(class_="grid product-meta-header")
        # if marca_item:
        #     product_information['Marca']=marca_item.text.strip()
            
        precio_item=product_container.find('h2',class_="jet-listing-dynamic-field__content")
        if precio_item:
            product_information['Precio']=precio_item.text.strip()

        
        
        patron=r'(\d+(\.\d+)?\s*(ml|lt|l))'
        coincidencia = re.search(patron, product_information['DescripcionCorta'].lower())
        if coincidencia:
        # Si se encontró una coincidencia, obtenemos el resultado completo
            resultado = coincidencia.group(1)
            product_information['Tamaño']=resultado

        imagen_item=product_container.find(class_="woocommerce-product-gallery__wrapper")
        if imagen_item:
            imagen_src=imagen_item.find('img',class_="zoomImg")
            product_information['Img']=imagen_src.get('src')


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
    URL = 'https://bp-peru.com/shop'
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


def scroll(driver):
    previous_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(30)
        time.sleep(10)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == previous_height:
            break
        
        previous_height = new_height
     

def productos_vinos(driver,fecha):
    INFORMANTE = 'BP-Peru'
    URL = 'https://bp-peru.com/shop'
    
    informacion=[]
    
    driver.get(URL)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="filters-column").find(class_="elementor-accordion-item")
    
    menu_items=menu.find_all(class_="jet-checkboxes-list__row jet-filter-row")
   
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="elementor-tab-content-4311"]/div/section/div/div/div/div/div/div/div/fieldset//input[@type="checkbox"]')))

    checkboxes = driver.find_elements(By.XPATH,'//*[@id="elementor-tab-content-4311"]/div/section/div/div/div/div/div/div/div/fieldset//input[@type="checkbox"]')
    
    counter=0
    total_pages=0
    
    product_links=[]
    for checkbox in checkboxes:
        wait = WebDriverWait(driver, 30)

        print('='*50)
        print(checkbox.get_attribute('data-label'))
        categoria=checkbox.get_attribute('data-label')
        driver.execute_script("arguments[0].click();", checkbox)
        
        driver.implicitly_wait(30)
        time.sleep(15)
        scroll(driver)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        container_products=soup.find(class_="elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-1e7ac88")
        product_grid=container_products.find(id="products-grid")
        
        sub_container=product_grid.find(class_="jet-listing-grid jet-listing")
        products=sub_container.find_all('div', {'data-widget_type': 'image.default'})
        for product in products:
            product_url=product.find('a')
            
            product_link=product_url.get('href')
            product_links.append((product_link,categoria))

            
        driver.execute_script("arguments[0].click();", checkbox)
        driver.implicitly_wait(30)
        time.sleep(15)
    
    for link in product_links:
   
        driver.get(link[0])
        time.sleep(7)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
  
        producto=agregar_informacion(soup,INFORMANTE,link[-1],fecha)
        if producto:
            counter+=1
            informacion.append(producto)
            print(counter)

                
    return informacion

def main(driver,stamped_today):
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()
    
    datos=productos_vinos(driver,stamped_today)
    filename=args.ruta + 'bp-peru_productos_'+stamped_today+'.csv'
    exportar_csv(datos,filename)                        
                
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

    main(driver,stamped_today)

    driver.quit()

    print(f"{time.time()-inicio}")

