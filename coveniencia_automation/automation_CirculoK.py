import os,datetime,json,time,requests,re,csv,argparse

# importar driver configurations
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# Import driver handlers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# import scrapping tool
from bs4 import BeautifulSoup


def scroll(driver, element_xpath, last_height):
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    for i in range(last_height, total_height, 50):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.25) 
    last_height = total_height   
    try:
        mostrar_mas = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, element_xpath))
        )
        mostrar_mas.click()
        time.sleep(2)
        print('Saltando a la siguiente pagina')
        return last_height, True
    except Exception as e:
        print('Fin de paginacion')
        return last_height, False


def productos_categorias(category_list,driver):
    # print('='*50,'\n','='*50)
    informacion=[]
    for category in category_list:
        print(category)
        link=category[-1]
        print(f"categoria {category[0]}")
        print(link)
        
        marcas=[]
        
        driver.get(link)
        time.sleep(3)
            
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        for checkbox in checkboxes:
            print(checkbox.get_attribute('name'))
            marcas.append(checkbox.get_attribute('name'))
        
        xpath="//a[div[contains(text(), 'Mostrar más')]]"
        finish_scroll = True
        last_height = driver.execute_script("return window.innerHeight")

        while finish_scroll:
            last_height, finish_scroll = scroll(driver, xpath, last_height)
        
        html_code=driver.page_source
        soup = BeautifulSoup(html_code,'html.parser')
        element_container=soup.find(id="gallery-layout-container")
        elements=element_container.find_all('a')
        print(f'productos totales {len(elements)}')

        informacion.append((category[0],marcas,elements))
       
            
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


def producto_informacion(soup_product,informante,categoria,marcas,fecha):
    product_information = {
        'Informante': informante,
        'Categoria':categoria,
        'DescripcionCorta':'',
        'Referencia':'',
        'Precio':'',
        'Promocion':'',
        'DescripcionLarga':'',
        'Tamaño':'',
        'Img':'',
        'Fecha':fecha
        }
    product_link = {
        'DescripcionCorta':'',
        'LinkProducto':''
    }
    url_base="https://www.contigock.com.mx/"
    
    print('producto informacion')
    
    descripcion_corta=soup_product.find('h1') #,class_="vtex-store-components-3-x-productNameContainer vtex-store-components-3-x-productNameContainer--prodNamePDP mv0 t-heading-4"
    if descripcion_corta:
        product_information['DescripcionCorta']=descripcion_corta.text.strip()
        # product_information['DescripcionLarga']=product_information['DescripcionCorta']
        product_information['Tamaño']=tamano_producto(product_information['DescripcionCorta'])
        product_link['DescripcionCorta']=product_information['DescripcionCorta']
    
    referencia=soup_product.find('span',class_="vtex-product-identifier-0-x-product-identifier__value")
    if referencia:
        product_information['Referencia']=referencia.text.strip('Referencia')
    
    precio=soup_product.find('span',class_="vtex-store-components-3-x-sellingPrice vtex-store-components-3-x-sellingPriceValue t-heading-2-s dib ph2 vtex-store-components-3-x-price_sellingPrice vtex-store-components-3-x-price_sellingPrice--prodPrice")
    if precio:
        product_information['Precio']=precio.text.strip()
    
    promocion=soup_product.find('span',class_="vtex-store-components-3-x-currencyContainer vtex-store-components-3-x-currencyContainer--prodPrice")
    if promocion:
        precio_promocion=promocion.text.strip()
        if precio_promocion == product_information['Precio']:
            product_information['Promocion']=''
        elif precio_promocion > product_information['Precio']:
            product_information['Promocion']=product_information['Precio']
            product_information['Precio']=precio_promocion
        
        
    imagen=soup_product.find('img',class_="vtex-store-components-3-x-productImageTag vtex-store-components-3-x-productImageTag--prodImage vtex-store-components-3-x-productImageTag--main vtex-store-components-3-x-productImageTag--prodImage--main")
    if imagen:
        product_information['Img']=imagen.get('src')
    
    descripcion_larga=soup_product.find('div',class_="vtex-store-components-3-x-container relative")
    if descripcion_larga:
        descripcion_text=descripcion_larga.text.strip()
        descripcion_lines=descripcion_text.splitlines()
        product_information['DescripcionLarga']=' '.join(descripcion_lines)
        
    link_producto=soup_product.find('a')
    if link_producto:
        product_link['LinkProducto']=url_base+link_producto.get('href')
    
    # for marca in marcas:
    #     if marca in product_information['DescripcionCorta']:
    #         product_information['Marca'] = marca
    #         break
        
    # print(json.dumps(product_information,indent=4))
    # print(json.dumps(product_link,indent=4))
    time.sleep(1)
    return product_information,product_link
          

def productos_informante(url,driver,fecha):
    informante='Circulo K'
    informacion=[]
    product_links=[]
    # driver.get(url)
    driver=click_mayor(driver,url)
    time.sleep(6)
    # driver.save_screenshot("captura_de_pantalla.png")
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    container = soup.find('div',class_="vtex-flex-layout-0-x-flexRow vtex-flex-layout-0-x-flexRow--Menu-Category-Content")
    categories = container.find_all('li')
    
    category_list=[]
    for category in categories:
        category_link_section=category.find('a')
        category_link=url[:-1]+category_link_section.get('href')
        categoria=category.text
        category_list.append((categoria,category_link))
         
    products=productos_categorias(category_list,driver)
    
    counter=0
    for product in products:
        # product(category, marcas,links)
        categoria=product[0]
        marcas=product[1]
        print(categoria)
        link_products=product[-1]
        for link_product in link_products:
            try:
                link_item=url[:-1]+link_product.get('href')
                driver.get(link_item)
                time.sleep(3)
                html = driver.page_source
                soup_product = BeautifulSoup(html, 'html.parser')
                
                product_info,product_link=producto_informacion(soup_product,informante,categoria,marcas,fecha)
                informacion.append(product_info)
                product_links.append(product_link)
                counter+=1
                print(counter)
            except:
                print(link_item)
    
    return informacion,product_links
    

def click_mayor(driver,link):
    driver.get(link)
    time.sleep(3)
    
    try:
        xpath_button="//button[div[contains(text(), 'Si')]]"
        button_yes = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,xpath_button)))
        button_yes.click()
    except Exception as e:
        print("Error: ", e)
        
    time.sleep(5)

    return driver


def main(driver,stamped_today):
    parser = argparse.ArgumentParser(description='Se incorpora la ruta destino del CSV')
    parser.add_argument('ruta', help='Ruta personalizada para el archivo CSV')
    args = parser.parse_args()
    
    URL="https://www.contigock.com.mx/"
    
    products,links=productos_informante(URL,driver,stamped_today)
    filename=args.ruta + 'productos_circuloK_'+stamped_today+'.csv' 
    
    exportar_csv(products,filename)


if __name__=='__main__':
    inicio=time.time()
    #
    # Chrome options for webdriver
    #
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
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")


    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service":False,
            "profile.password_manager_enabled":False
        }
    )

    # Install Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)
    
    today = datetime.datetime.now()
    stamped_today = today.strftime("%Y-%m-%d")
    
    main(driver,stamped_today)
    

    driver.quit()