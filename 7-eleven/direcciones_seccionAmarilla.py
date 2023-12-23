import csv, re, os, json, datetime, json, time, requests
import googlemaps

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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


def limpiar_texto(texto, caracteres_a_eliminar):
    for char in caracteres_a_eliminar:
        texto = texto.replace(char, "")
    return texto


def direcciones(soup,informante,fecha):
    
    caracteres_eliminar = ['-', '"']
            
    tienda={
        'Informante':informante,
        'Ciudad':'',
        'Direccion':'',
        'Colonia':'',
        'CP':'',
        'Latitud':'',
        'Longitud':'',
        'Telefono':'',
        'fecha':fecha
    }

    titulo= soup.find('span', {'itemprop': 'name'})
    if informante in titulo:
        direccion_texto=soup.find('div', class_='l-address')
        if direccion_texto:
            direccion_=direccion_texto.text.strip()   
            tienda['Direccion']=limpiar_texto(direccion_.strip(),caracteres_eliminar)
            direccion_lineas=direccion_.split(',')
            
            longitud,latitud = geolocalizacion(tienda['Direccion'])
            tienda['Latitud'] = latitud
            tienda['Longitud'] = longitud
            
            try:
                tienda['CP']=direccion_lineas[-1].strip()
                tienda['Ciudad'] = direccion_lineas[2].strip()
                tienda['Colonia'] = direccion_lineas[1].strip()
            except:
                print(f'error en {direccion_}')
                
        telefono=soup.find(class_="l-tel")
        if telefono:
            tienda['Telefono']=telefono.text.strip()

        print(json.dumps(tienda,indent=4))
    
        return tienda
    else:
        return None


def find_term(driver,term):
    
    try:
        search_box = driver.find_element(By.ID, 'typefield')
        search_box.clear()
    except:
        search_box = driver.find_element(By.ID, 'typed')
        search_box.clear()
    finally:
        for i in term:
            search_box.send_keys(i)
            time.sleep(.35)
        
        search_box.send_keys(Keys.RETURN)
        return driver
        

def get_results(driver):
    paginacion=True
    soups=[]
    
    html_code=driver.page_source
    soup=BeautifulSoup(html_code,'html.parser')
    not_found=soup.find(class_='noFound')
    
    if not_found:
        return []
    while paginacion:
        
        html_code=driver.page_source
        soup=BeautifulSoup(html_code,'html.parser')
        soups.append(soup)
        driver,paginacion=next_page(driver)
        time.sleep(5)
        
    return soups


def next_page(driver):
    try:
        siguiente_button = driver.find_element(By.XPATH,'//a[@title="Siguiente"]')
        siguiente_button.click()
        return driver, True
    except:
        return driver, False

        
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
    
    URL="https://www.seccionamarilla.com.mx/resultados/oxxo/1"
    terminos=['7 eleven','circulo k','oxxo']
    ciudades=["Luvianos","Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas",'Chihuahua','Coahuila','Colima','Durango', 'Guanajuato','Guerrero','Hidalgo','Jalisco','Michoacán','Morelos','Nayarit','Nuevo León','Oaxaca','Puebla','Querétaro','Quintana Roo','San Luis Potosí','Sinaloa','Sonora','Tabasco','Tamaulipas','Tlaxcala','Veracruz','Yucatán', 'Zacatecas','Álvaro Obregón','Azcapotzalco','Benito Juárez','Cuajimalpa de Morelos','Coyoacán','Cuauhtémoc','Gustavo A Madero','Iztacalco','Iztapalapa','La Magdalena Contreras','Miguel Hidalgo','Milpa Alta','Tláhuac','Tlalpan','Venustiano Carranza','Xochimilco',"Papalotla", "Otzoloapan","Zacazonapan","Texcalyacac","Ixtapan del Oro","San Simón de Guerrero","Santo Tomás","Ayapango","Nopaltepec","Ecatzingo","Tenango del Aire","Isidro Fabela","Almoloya del Río","Chapultepec","Tonatico","Atizapán","Zacualpan","Mexicaltzingo","Temamatla","Soyaniquilpan de Juárez","Tonanitla","Polotitlán","Cocotitlán","Almoloya de Alquisiras","Joquicingo","Rayón","Timilpan","Texcaltitlán","Zumpahuacán","Jilotzingo","Tepetlixpa","Amanalco","Sultepec","Amatepec","Juchitepec","Chiconcuac","Malinalco","Jaltenco","Axapusco","San Martín de las Pirámides","Chiautla","Xalatlaco","Ozumba","Chapa de Mota","Tlatlaya","Apaxco","Atlautla","San Antonio la Isla","Tepetlaoxtoc","Temascaltepec","Ocuilan","Otumba","Ixtapan de la Sal","Capulhuac","El Oro","Donato Guerra","Coatepec Harinas","Tequixquiac","Coyotepec","Temascalapa","Hueypoxtla","Tezoyuca","Tlalmanalco","Aculco","Villa del Carbón","Villa de Allende","Amecameca","Xonacatlán","Nextlalpan","Teotihuacán","Melchor Ocampo","Valle de Bravo","Teoloyucan","Temascalcingo","Acambay","Calimaya","Villa Guerrero","Jocotitlán","Ocoyoacac","Atenco","Jiquipilco","Tejupilco","Tianguistenco","Jilotepec","Otzolotepec","Tenango del Valle","San Mateo Atenco","San José del Rincón","Tepotzotlán","Tenancingo","Temoaya","Villa Victoria","Atlacomulco","San Felipe del Progreso","Tultepec","Ixtlahuaca","Huehuetoca","Lerma","Acolman","Almoloya de Juárez","Cuautitlán","Chicoloapan","Zinacantepec","Metepec","Texcoco","Zumpango","Huixquilucan","Coacalco de Berriozábal","La Paz","Valle de Chalco","Chalco","Nicolás Romero","Tultitlán","Atizapán de Zaragoza","Ixtapaluca","Tecámac","Cuautitlán Izcalli","Tlalnepantla de Baz","Chimalhuacán","Naucalpan de Juárez","Toluca","Nezahualcóyotl","Ecatepec de Morelos"
]

    driver.get(URL)
    time.sleep(5)
    
    for termino in terminos:
        directorio=[]
        counter=0
        filename=f'sucursaes_{termino}_{stamped_today}.csv'

        for ciudad in ciudades:
            termino_busqueda=f'{termino} en {ciudad}'
            driver=find_term(driver,termino_busqueda)
            time.sleep(10)
            soups=get_results(driver)
            for soup in soups:
                
                list_container=soup.find('ul',class_="list")
                address_elements=list_container.find_all('li')
                for element in address_elements:
                    direccion=direcciones(element,termino,stamped_today)
                    if direccion:
                        directorio.append(direccion)
                        counter+=1
                        print(counter)
        exportar_csv(directorio,filename)
    driver.quit()