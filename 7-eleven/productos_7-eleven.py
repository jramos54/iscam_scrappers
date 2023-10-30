import os
import datetime
import json,re,csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scroll(driver, element_xpath):
    
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    
    for i in range(1, total_height, 50):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.25)
    
    # driver.save_screenshot("bottom_page.png")
    
    try:
        link = driver.find_element(By.XPATH, element_xpath)
        ActionChains(driver).move_to_element(link).click().perform()
        time.sleep(5)
        print('Saltando a la siguiente pagina')
        return True
    except Exception as e:
        print('Fin de paginacion')
        return False


def productos_categorias(category_list,driver):
    informacion=[]
    for category in category_list:
        link=category[-1]
        print(category[0])
        print(link)
        
        driver.get(link)
        time.sleep(3)
        
        #element_xpath = "//a[contains(@class, 'vtex-button') and contains(text(), 'Mostrar más')]"
        xpath='/html/body/div[2]/div/div[1]/div/div[2]/div/div/section/div[2]/div/div[3]/div/div[2]/div/div[4]/div/div/div/div/div/a'
        finish_scroll=True
        while finish_scroll:
            finish_scroll=scroll(driver, xpath)
            
        html_code=driver.page_source
        soup = BeautifulSoup(html_code,'html.parser')
        elements=soup.find_all(class_="vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4")
        print(f'productos totales {len(elements)}')
        informacion.append((category[0],elements))
    return informacion


def tamano_producto(cadena):
    match = re.search(r'\d+\s*[A-Za-z]+', cadena)
    
    if match:
        return match.group()
    else:
        return ''


def exportar_csv(diccionarios, nombre_archivo):
    # Obtener las claves del primer diccionario para definir los encabezados del CSV
    encabezados = diccionarios[0].keys()

    with open(nombre_archivo, 'w', newline='',encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=encabezados, delimiter='|')

        # Escribir los encabezados en la primera línea del CSV
        writer.writeheader()

        # Escribir cada diccionario como una línea en el CSV
        for diccionario in diccionarios:
            writer.writerow(diccionario)


def producto_informacion(soup_product,informante,categoria,fecha):
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'DescripcionCorta':'',
        'Precio':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    product_link = {
        'DescripcionCorta':'',
        'LinkProducto':''
    }
    url_base='https://www.tiendaenlinea.7-eleven.com.mx'
    
    
    descripcion_corta=soup_product.find('h3')
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text.strip()
        product_information['DescripcionLarga']=product_information['DescripcionCorta']
        product_information['Tamaño']=tamano_producto(product_information['DescripcionCorta'])
        product_link['DescripcionCorta']=product_information['DescripcionCorta']
    
    precio=soup_product.find('span',class_="vtex-product-price-1-x-sellingPrice vtex-product-price-1-x-sellingPrice--summary")
    if precio:
        product_information['Precio']=precio.text.strip()
        
    imagen=soup_product.find('img')
    if imagen:
        product_information['Img']=imagen.get('src')
        
    link_producto=soup_product.find('a')
    if link_producto:
        product_link['LinkProducto']=url_base=link_producto.get('href')
        
    print(json.dumps(product_information,indent=4))
    print(json.dumps(product_link,indent=4))
    
    return product_information,product_link
          

def productos_informante(url,driver,fecha):
    informante='7-eleven'
    informacion=[]
    product_links=[]
    driver.get(url)
    
    time.sleep(6)
    # driver.save_screenshot("captura_de_pantalla.png")

    menu_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-id='mega-menu-trigger-button']")))
    time.sleep(2)
    menu_button.click()
    time.sleep(3)
    
    print(menu_button.text)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    section_1=soup.find(class_="render-container render-route-store-home")
    section_2=section_1.find(class_="flex flex-column min-vh-100 w-100")
    section_3=section_2.find(class_="vtex-flex-layout-0-x-flexRow vtex-flex-layout-0-x-flexRow--main-header")

    categories=section_2.find_all('li',class_="vtex-mega-menu-2-x-menuItem")
    
    category_list=[]
    for category in categories:
        category_link=category.find('a')
        category_list.append((category.text,category_link.get('href')))
    
    products=productos_categorias(category_list,driver)
    
    for product in products:
        categoria=product[0]
        soup_product=product[-1]
        product_info,product_link=producto_informacion(soup_product,informante,categoria,fecha)
        informacion.append(product_info)
        product_links.append(product_link)
    
    return informacion,product_links
    
    
if __name__=='__main__':
    inicio=time.time()
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
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
    
    URL="https://www.tiendaenlinea.7-eleven.com.mx/"
    file_name='productos_7-eleven'+stamped_today+'.csv'
    
    products,links=productos_informante(URL,driver,stamped_today)
    exportar_csv(products,file_name)
    
    driver.quit()