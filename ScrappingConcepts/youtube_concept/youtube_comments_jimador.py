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
from selenium.webdriver.common.keys import Keys


# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from lxml import etree
import pyautogui

# def scroll(driver):
#     print('scroll',end='\n\n')
#     total_height = driver.execute_script("return document.documentElement.scrollHeight;")
#     current_scroll_position = scroll_position = driver.execute_script("return window.pageYOffset;")
#     print(total_height, current_scroll_position)
#     while True:
#         for i in range(current_scroll_position, total_height, 50):
#             driver.execute_script("window.scrollTo(0, {});".format(i))
#             time.sleep(0.25)
#             current_scroll_position = scroll_position = driver.execute_script("return window.pageYOffset;")
#             print(current_scroll_position)
#         current_scroll_position = scroll_position = driver.execute_script("return window.pageYOffset;")
#         total_height = driver.execute_script("return document.documentElement.scrollHeight;")
#         if current_scroll_position==total_height:
#             break
        
def scroll(driver):
    print('scroll', end='\n\n')
    last_position = driver.execute_script("return window.pageYOffset;")
    
    while True:
        # Scroll hacia abajo en incrementos de 50px
        driver.execute_script("window.scrollBy(0, 50);")
        time.sleep(0.25)
        
        # Obtener la posición actual del scroll
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        print(current_scroll_position)
        
        # Verificar si hemos llegado al final
        if current_scroll_position == last_position:
            break
        last_position = current_scroll_position

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
  
def video_search(driver,keyword):
    print('video search')
    xpath_element='/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/form/div[1]/div[1]/input'
    search_box=driver.find_element(By.XPATH,xpath_element)
    
    for key in keyword:
        search_box.send_keys(key)
        time.sleep(.75)
    search_box.send_keys(Keys.RETURN)

def search_results(driver):
    html_results=driver.page_source
    
    tree = etree.HTML(html_results)
    xpath_element='/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer[2]'
    elements=tree.xpath(xpath_element)
    
    target_urls=[]
    if elements:
        soup=BeautifulSoup(etree.tostring(elements[0]),'html.parser')
        
        contents_container=soup.find(id='contents')
        contents=contents_container.find_all(id="video-title")
# --------------------  Arreglar el scroll ----------------------------------------
        scroll(driver)
# ---------------------------------------------------------------------------------

        print(len(contents))
        for content in contents:
            titulo=content.get('title')
            print(titulo)
            link='https://www.youtube.com'+content.get('href')
            print(link)
            target_urls.append((titulo,link))
            print('='*50)
    return target_urls

def video_properties(driver):
    comments=video_comments(driver)
    data=video_information(driver)
    
    video_data={'comments':comments,
                'data':data}
    return video_data
    
def video_comments(driver):
    print('getting video comments')
    xpath_comments_container='/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-comments'
    
    scroll(driver)
    
    html_results=driver.page_source
    
    tree = etree.HTML(html_results)
    # elements=tree.xpath(xpath_comments_container)
    # print(elements[0])
    
    # xpath_comments_container='/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-comments/ytd-item-section-renderer/div[3]'
    comments_container=tree.xpath(xpath_comments_container)
    
    comments_data=[]
    if comments_container:
        print('find elements comments')
        soup=BeautifulSoup(etree.tostring(comments_container[0]),'html.parser')
        print(soup)
        comments=soup.find_all(class_="style-scope ytd-item-section-renderer",recursive=False)
            
        for comment in comments:
                
            print(comment)
            print(comment.text)

def video_information(driver):
    pass

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
    
    URL="https://www.youtube.com/"
    file_name='comments'+stamped_today+'.csv'
    try:
        driver.get(URL)
        time.sleep(10)
        html=driver.page_source

        # with open('page.html','w',encoding='utf-8') as f:
        #     f.write(html)
            
        video_search(driver,'tequila jimador')
        time.sleep(10)
        urls=search_results(driver)
        
        for url in urls:
            driver.get(url[-1])
            time.sleep(10)
            data=video_properties(driver)
            print(json.dumps(data,indent=2))
            
        time.sleep(30)
        driver.quit()
    except Exception as e:
        print(e)
        driver.quit()