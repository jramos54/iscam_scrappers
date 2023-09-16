import os
import datetime
import json
import time
import requests
import re
import csv

# Importar Selenium webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# importar webdriver manager
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

#  1. Loads the html data
#  2. Turns it into soup
def load_data(driver, linkPage):
    # Get the contents of the URL
    driver.get(linkPage)
    time.sleep(35)
    # returns the inner HTML as a string
    innerHTML = driver.page_source
    # turns the html into an object to use with BeautifulSoup library
    soup = BeautifulSoup(innerHTML, "html.parser")
    get_data_list(soup)

# gets the product price
def get_data_list(soup):
    elements = soup.find_all('div', class_="itemBox-container-wrp")

    elements = elements + soup.find_all('div', class_="itemBox-container-wrp grid-itemBox-wrp first newAtc-itemBox-container-wrp osmosis")
    elements = elements + soup.find_all('div', class_="itemBox-container-wrp grid-itemBox-wrp newAtc-itemBox-container-wrp osmosis")
    elements = elements + soup.find_all('div', class_="itemBox-container-wrp grid-itemBox-wrp last newAtc-itemBox-container-wrp osmosis")

    global collected_data_clicores
    # if not elements:
    for items in elements:
        old_price = items.find('div', class_="item-oldprice")
        if old_price is not None:
            old_price = items.find('div', class_="item-oldprice").find("span",class_="normal strikeOffRequire").getText()
            old_price = old_price + '.' + items.find('div', class_="item-oldprice").find("span",class_="sup").getText()

        new_price = items.find('div', class_="item-newprice new-price-content").find("span", class_="normal").getText()
        new_price = new_price + '.' + items.find('div', class_="item-newprice new-price-content").find("span", class_="sup").getText()

        if old_price is not None:
            price = old_price
            promo = new_price
        else:
            price = new_price
            promo = ""

        collected_data_clicores = collected_data_clicores + [
            {
                "CLUB": 'Sams',
                "PRODUCTO": items.find('a', class_="item-name").get('title'),
                "PRECIO_NORMAL": price,
                "PRECIO_PROMOCION": promo,
            }
        ]

# Create final file, data to csv
def create_output_file():
    field_names = ["CLUB", "PRODUCTO", "PRECIO_NORMAL", "PRECIO_PROMOCION"]
    with open('SamsPriceList.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for i in collected_data_clicores:
            writer.writerow(i)
            print(i)

if __name__=='__main__':
    inicio=time.time()
    # Obtener la ruta absoluta del directorio actual del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en segundo plano
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--log-level=3") # no mostar log

    driver_path = os.path.join(parent_dir, "chromedriver")  # Ruta al chromedriver

    os.environ["WDM_LOCAL"] = '1'
    os.environ["WDM_PATH"] = driver_path

    driver_manager = ChromeDriverManager().install()
    

    driver = webdriver.Chrome(service=Service(driver_manager), options=chrome_options)

    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")

    links=[
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/brandy/_/N-8xs',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/cognac/_/N-8y2',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/cocteleria/cremas-y-licores/_/N-a9m',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/mezcal/_/N-9ey',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/ron/_/N-8xx',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/tequila/_/N-8xy',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/vodka/_/N-8yb',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/licores/whisky/_/N-8xu',
        'https://www.sams.com.mx/vinos-licores-y-cervezas/cocteleria/jarabes-y-mezcladores/_/N-a9k'
    ]

    collected_data_clicores=[]

    for link in links:
        print(link)
        load_data(driver,link)
        create_output_file()
    
    driver.quit()

    print(f"{time.time()-inicio}")