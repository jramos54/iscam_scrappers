import os
import datetime
import json,re,csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

        
def scroll(driver,last_height):
    
    total_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(last_height, total_height, 55):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.25)
        
            
    return total_height


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
            

def login_fb(driver):
    print('login ...')
    USER='5561774972'
    PASSWORD='Arioto02'
    user=driver.find_element(By.ID,'email')
    for i in USER:
        user.send_keys(i)
        time.sleep(.35)
    password=driver.find_element(By.ID,'pass')
    for i in PASSWORD:
        password.send_keys(i)
        time.sleep(.35)
    login_button=driver.find_element(By.XPATH, '//button[@data-testid="royal_login_button"]')
    time.sleep(2)
    login_button.click()
    return driver
    
def search_term(driver,search_word):
    print('searching word...')
    elemento_buscar = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Buscar en Facebook"]')
    for i in search_word:
        elemento_buscar.send_keys(i)
        time.sleep(.35)
    
    elemento_buscar.send_keys(Keys.RETURN)
    time.sleep(3)
    return driver

def get_comments(raw_soups):
    print('getting comments...')
    for soup in raw_soups:
        comments_container=soup.find(class_="x1gslohp")
        comments=comments_container.find_all('div')
        print(comments.text)


def get_cards(driver):
    print('clicking comments...')
    xpath_comments="//span[contains(text(), 'comentario')]"
    soups=[]
    print('scroll starting ...')
    last_height = driver.execute_script("return window.innerHeight")
    total_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(last_height, total_height, 15):
        print('scrolling ...')
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.25)
        print('click on comments comments...')
        comment_element = driver.find_element(By.XPATH,xpath_comments)
        if comment_element:
            driver.execute_script("arguments[0].scrollIntoView(true);", comment_element)
            print(comment_element.location)
            driver.execute_script("arguments[0].click();", comment_element)
            #comment_element.click()
            time.sleep(5)
            html_code=driver.page_source
            soup=BeautifulSoup(html_code,'html.parser')
            print(soup.text)
            soups.append(soup)
        last_height = driver.execute_script("return window.innerHeight")
        
    
    
    
    # comment_elements = driver.find_elements(By.XPATH,xpath_comments)
    
    # print(f'total comments gathered {len(comment_elements)}')
    # for comment in comment_elements:
    #     comment.click()
    #     time.sleep(5)
    #     html_code=driver.page_source
    #     soup=BeautifulSoup(html_code,'html.parser')
    #     print(soup.text)
    #     soups.append(soup)
    return soups

def main(driver,url):
    driver.get(url)
    time.sleep(5)
    driver=login_fb(driver)
    time.sleep(2)
    driver=search_term(driver,'tequila jimador')
    time.sleep(2)
    soups=get_cards(driver)
    time.sleep(2)
    comments=get_comments(soups)
    

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
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-geolocation")
    chrome_options.add_argument("--disable-features=PasswordImport")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    chrome_service = ChromeService(driver_manager.install())  # Esto descargará el ejecutable de ChromeDriver

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    today = datetime.datetime.now()
    stamped_today = today.strftime("%Y-%m-%d")
    
    URL="https://www.facebook.com/"
    file_name='comments'+stamped_today+'.csv'
    try:
        main(driver,URL)
        time.sleep(15)
        driver.quit()
    except Exception as e:
        print(e)
        driver.quit()