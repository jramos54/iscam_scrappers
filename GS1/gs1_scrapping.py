import os,datetime,json,time,requests,re,csv,logging
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


def driver_configuration(logger:logging):
    logger.info('==> Driver configuration ...')
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-urlfetcher-cert-requests")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--js-flags=--max-old-space-size=4096')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--password-store=basic')
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service":False,
            "profile.password_manager_enabled":False
        }
    )
    
    
    # Instalar o cargar el controlador Chrome WebDriver
    driver_manager = ChromeDriverManager()
    driver = webdriver.Chrome(service=Service(executable_path=driver_manager.install()), options=chrome_options)
    
    return driver


def logger_configuration(stamped_today:str):
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('GS1 Logging')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_name='GS1_log'+stamped_today+'.log'
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.INFO) 
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def login(driver:webdriver, logger:logging):
    URL='https://login.syncfonia.com/home'
    Usuario = '7508006015651'
    Contraseña = 'I1payfxuw#'
    logger.info(f'==> Log in in page {URL}')
    
    driver.get(URL)
    
    logger.info("Input username")
    username_box=driver.find_element(By.ID,'username')
    for char in Usuario:
        username_box.send_keys(char)
        time.sleep(.35)
        
    logger.info("Input pasword")
    password_box=driver.find_element(By.ID,'password')
    for char in Contraseña:
        password_box.send_keys(char)
        time.sleep(.35)
    
    # button_xpath='/html/body/div/main/section/div/div/div/form/div[3]/button'
    login_button=driver.find_element(By.CSS_SELECTOR,'button[type="submit"]')
    login_button.click()
    time.sleep(2)
    
    return driver


def goto_search(driver:webdriver,logger:logging):
    
    logger.info("==> Click into search icon...")
    wait=WebDriverWait(driver,10)
    sahdow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root MAIN")
    time.sleep(2)
    
    shadow_app=sahdow_main.find_element(By.CSS_SELECTOR,'app-common').shadow_root
    #logger.info("Activating shadow-root APP")
    time.sleep(2)

    shadow_menu=shadow_app.find_element(By.CSS_SELECTOR,'#drawerNavLayout')
    #logger.info("Activating shadow-root MENU")
    time.sleep(2)

    shadow_nav_menu=shadow_menu.find_element(By.CSS_SELECTOR,'rock-navmenu').shadow_root
    #logger.info("Activating shadow-root NAV MENU")
    time.sleep(2) 
    
    menu_content=shadow_nav_menu.find_element(By.CSS_SELECTOR,'div.drawer-content')
    menu_element=menu_content.find_element(By.ID,'mainMenu')
    #logger.info("elements for the search icon activated...")
    
    search_icon=menu_element.find_element(By.ID,"menuIcon 3")
    search_icon.click()
    #logger.info("Showing the search button element")

    time.sleep(2)
    
    shadow_dropdown=menu_element.find_element(By.ID,'pebbleActionDropdown').shadow_root
    actions_element=shadow_dropdown.find_element(By.CSS_SELECTOR,'#actionsPopover')
    #logger.info("Search Domain activated...")

    action_item=actions_element.find_element(By.ID,'actionItem')
    action_item.click()
    time.sleep(10)
    
    return driver


def check_all(driver,logger):
    
    logger.info("==> Checking all elements...")
    wait=WebDriverWait(driver,10)
    sahdow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root" + 'main-app'.upper())
    time.sleep(2)   
    
    shadow_content=sahdow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-discovery').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_grid=shadow_container.find_element(By.CSS_SELECTOR,'#entitySearchDiscoveryGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchDiscoveryGrid'.upper())
    
    shadow_entity_grid=shadow_grid.find_element(By.CSS_SELECTOR,'#entitySearchGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchGrid'.upper())
    
    shadow_entity=shadow_entity_grid.find_element(By.CSS_SELECTOR,'#entityGrid').shadow_root
    #logger.info("Activating shadow-root "+'entityGrid'.upper())
    
    shadow_grid_container=shadow_entity.find_element(By.CSS_SELECTOR,'pebble-grid').shadow_root
    #logger.info("Activating shadow-root "+'pebble-grid'.upper())
    
    grid_container=shadow_grid_container.find_element(By.CSS_SELECTOR,'#grid').shadow_root
    #logger.info("Activating shadow-root "+'grid'.upper())
    
    grid_selection=grid_container.find_element(By.CSS_SELECTOR,'grid-selection-options').shadow_root
    #logger.info("Activating shadow-root "+'grid-selection-options'.upper())
    
    shadow_checker=grid_selection.find_element(By.CSS_SELECTOR,'#headerCheckbox').shadow_root
    #logger.info("Activating shadow-root "+'headerCheckbox'.upper())
    
    check_box=shadow_checker.find_element(By.CSS_SELECTOR,'#checkboxContainer')
    #logger.info("Accessing to "+'checkboxContainer'.upper())
    
    check_box.click()
    logger.info("Clicking to the button "+'checkboxContainer'.upper())
    time.sleep(5)
    
    return driver
    
def selected_comparison(driver,logger):
    pass

def scroll_down(driver,logger):
    logger.info("==> Starting the scroll process...")

    finish_scroll = False
    # last_height = driver.execute_script("return window.innerHeight")
    # logger.info(f"inner heigth {last_height}")
    while not finish_scroll:
        finish_scroll, driver = scroll(driver,logger)
    
    return driver
    
    
def scroll(driver,logger): 
    logger.info("==> Doing scrolling...")

       
    
    # logger.info(f"total height - {total_height}")   
    wait=WebDriverWait(driver,10)
    sahdow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root" + 'main-app'.upper())
    time.sleep(2)   
    
    shadow_content=sahdow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-discovery').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_grid=shadow_container.find_element(By.CSS_SELECTOR,'#entitySearchDiscoveryGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchDiscoveryGrid'.upper())
    
    shadow_search_grid=shadow_grid.find_element(By.CSS_SELECTOR,'#entitySearchGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchGrid'.upper())
    
    shadow_entity_grid=shadow_search_grid.find_element(By.CSS_SELECTOR,'#entityGrid').shadow_root
    #logger.info("Activating shadow-root "+'entityGrid'.upper())
    
    grid_container=shadow_entity_grid.find_element(By.CSS_SELECTOR,'#pebbleGridContainer')
    shadow_grid_container=grid_container.find_element(By.CSS_SELECTOR,'pebble-grid').shadow_root
    
    inner_container=shadow_grid_container.find_element(By.CSS_SELECTOR,'#pebbleGridContainer')
    
    shadow_inner_grid=inner_container.find_element(By.CSS_SELECTOR,'#grid').shadow_root
    lit_grid=shadow_inner_grid.find_element(By.CSS_SELECTOR,'#lit-grid')
    
    grid_elements=lit_grid.find_element(By.CSS_SELECTOR,'div.ag-body-viewport.ag-layout-normal.ag-row-no-animation')
    
    driver.execute_script("arguments[0].scrollTop += arguments[1];", grid_elements, 1000)

    total_selected,total_items=get_totals(driver,logger)
    
    finished_scrolling = total_selected == total_items
    # finished_scrolling = total_selected == "350"

    
    return finished_scrolling,driver
    

def get_totals(driver,logger):
    
    logger.info("==> Checking totals and total selected...")
    
    wait=WebDriverWait(driver,10)
    sahdow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root" + 'main-app'.upper())
    time.sleep(2)   
    
    shadow_content=sahdow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-discovery').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_grid=shadow_container.find_element(By.CSS_SELECTOR,'#entitySearchDiscoveryGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchDiscoveryGrid'.upper())
    
    shadow_search_grid=shadow_grid.find_element(By.CSS_SELECTOR,'#entitySearchGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchGrid'.upper())
    
    shadow_entity_grid=shadow_search_grid.find_element(By.CSS_SELECTOR,'#entityGrid').shadow_root
    #logger.info("Activating shadow-root "+'entityGrid'.upper())
    
    header=shadow_entity_grid.find_element(By.CSS_SELECTOR,'#gridHeader')
    #logger.info("Activating shadow-root "+'gridHeader'.upper())
    
    selected_element=header.find_element(By.CSS_SELECTOR,"#selection-title")
    selected_text=selected_element.text.split(" ")
    total_selected=selected_text[0]
    logger.info(f"Total selected = {total_selected}")

    total_items=None
    elements_container=header.find_elements(By.TAG_NAME,"div")
    
    span_elements=elements_container[1].find_elements(By.TAG_NAME,"span") 
    for span in span_elements:
        if span.get_attribute('title'):
            totals_element=span.text
            totals_text=totals_element.split('/')
            total_items=totals_text[-1].strip()
            logger.info(f"Total elements = {total_items}")

    return total_selected, total_items


def download_button(driver,logger):
    
    logger.info("==> Clicking to the download icon...")
    
    wait=WebDriverWait(driver,10)
    sahdow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root" + 'main-app'.upper())
    time.sleep(2)   
    
    shadow_content=sahdow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-discovery').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_grid=shadow_container.find_element(By.CSS_SELECTOR,'#entitySearchDiscoveryGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchDiscoveryGrid'.upper())
    
    shadow_entity_grid=shadow_grid.find_element(By.CSS_SELECTOR,'#entitySearchGrid').shadow_root
    #logger.info("Activating shadow-root "+'entitySearchGrid'.upper())

    search_result_bar=shadow_entity_grid.find_element(By.CSS_SELECTOR,'#gridActions').shadow_root
    #logger.info("Activating shadow-root "+'gridActions'.upper())
    
    toolbar_actions=search_result_bar.find_element(By.CSS_SELECTOR,'#searchResultToolbar').shadow_root
    #logger.info("Activating shadow-root "+'searchResultToolbar'.upper())
    
    shadow_actions=toolbar_actions.find_element(By.CSS_SELECTOR,'#toolbar_actions')
    #logger.info("Clicking to  "+'toolbar_actions'.upper())
    
    shadow_actions.click()
    time.sleep(5)
    
    return driver
   

def download_all(driver,logger):
    # TODO ==> hace falta definir la ruta de descarga en selenium
    
    logger.info("==> Clicking to the download all button...")
    
    wait=WebDriverWait(driver,10)
    shadow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root " + 'main-app'.upper())
    time.sleep(2) 
    
    shadow_app=shadow_main.find_element(By.CSS_SELECTOR,'app-common').shadow_root
    #logger.info("Activating shadow-root " + 'app-common'.upper())
    
    shadow_dialog=shadow_app.find_element(By.CSS_SELECTOR,'#contextDialog').shadow_root
    #logger.info("Activating shadow-root " + 'contextDialog'.upper())
    
    shadow_wizard=shadow_dialog.find_element(By.CSS_SELECTOR,'#rockWizardManage').shadow_root
    #logger.info("Activating shadow-root " + 'rockWizardManage'.upper())
    
    shadow_rock=shadow_wizard.find_element(By.CSS_SELECTOR,'rock-scope-manage').shadow_root
    #logger.info("Activating shadow-root " + 'rock-scope-manage'.upper())
    
    content_actions=shadow_rock.find_element(By.CSS_SELECTOR,'#content-actions')
    #logger.info("Accessing to " + 'content-actions'.upper())
    
    download_button=content_actions.find_element(By.CSS_SELECTOR,'#DownloadAll')
    download_button.click()
    logger.info("Clicking to  " + 'DownloadAll'.upper())
    
    time.sleep(2)
    return driver


def wait_download(driver,logger):
    driver=task_details(driver,logger)
    status=False
    
    while not status:
        time.sleep(30)
        driver=refresh_button(driver,logger)
        driver,status=complete_status(driver,logger)
        
    
    driver=download_file(driver,logger)
    return driver


def task_details(driver,logger):
    logger.info("==> Clicking to the task details button...")
    
    wait=WebDriverWait(driver,10)
    shadow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root " + 'main-app'.upper())
    time.sleep(2) 
    
    shadow_app=shadow_main.find_element(By.CSS_SELECTOR,'app-common').shadow_root
    #logger.info("Activating shadow-root " + 'app-common'.upper())
    
    shadow_dialog=shadow_app.find_element(By.CSS_SELECTOR,'#contextDialog').shadow_root
    #logger.info("Activating shadow-root " + 'contextDialog'.upper())
    
    shadow_wizard=shadow_dialog.find_element(By.CSS_SELECTOR,'#rockWizardManage').shadow_root
    #logger.info("Activating shadow-root " + 'rockWizardManage'.upper())
    
    shadow_rock=shadow_wizard.find_element(By.CSS_SELECTOR,'rock-business-function-finish').shadow_root
    #logger.info("Activating shadow-root " + 'rock-scope-manage'.upper())
    
    user_actions=shadow_rock.find_element(By.CSS_SELECTOR,'#user-actions')
    
    details_button=user_actions.find_element(By.CSS_SELECTOR,'pebble-button[button-text="Show task details"]')
    details_button.click()
    
    return driver
    

def complete_status(driver,logger):
    logger.info("==> Checking the status...")
    
    wait=WebDriverWait(driver,10)
    shadow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root " + 'main-app'.upper())
    time.sleep(2) 
    
    shadow_content=shadow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-manage').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_header=shadow_container.find_element(By.CSS_SELECTOR,'#entityManageHeader').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    status_div=shadow_header.find_element(By.CSS_SELECTOR,'div[name="status"]')
    
    status_val=status_div.find_element(By.CSS_SELECTOR,'#attrVal')
    current_status=status_val.text.strip()
    
    if current_status=="Completed":
        return driver, True
    else:
        return driver,False
    

def refresh_button(driver,logger):
    logger.info("==> Clicking to the refresh button...")
    
    wait=WebDriverWait(driver,10)
    shadow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root " + 'main-app'.upper())
    time.sleep(2) 
    
    shadow_content=shadow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-manage').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_header=shadow_container.find_element(By.CSS_SELECTOR,'#entityManageHeader').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    shadow_actions=shadow_header.find_element(By.CSS_SELECTOR,'#entityActions').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    shadow_toolbar=shadow_actions.find_element(By.CSS_SELECTOR,'#toolbar').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    refresh_button_task=shadow_toolbar.find_element(By.CSS_SELECTOR,'pebble-button[title="Refresh"]')
    
    refresh_button_task.click()
    
    return driver


def download_file(driver,logger):
    logger.info("==> Clicking to the download button...")
    
    wait=WebDriverWait(driver,10)
    shadow_main=wait.until(EC.presence_of_element_located((By.TAG_NAME,'main-app'))).shadow_root
    #logger.info("Activating shadow-root " + 'main-app'.upper())
    time.sleep(2) 
    
    shadow_content=shadow_main.find_element(By.CSS_SELECTOR,'#contentViewManager').shadow_root
    #logger.info("Activating shadow-root "+'contentViewManager'.upper())
    
    shadow_subcontent=shadow_content.find_element(By.CSS_SELECTOR,'#contentViewManager')
    #logger.info("Accessing to "+'contentViewManager'.upper())
    
    rock_contents=shadow_subcontent.find_elements(By.CSS_SELECTOR,'rock-content-view')
    #logger.info("Accessing to "+'rock-content-view'.upper())
    time.sleep(2)
    
    shadow_content_view=rock_contents[-1].shadow_root
    #logger.info("Activating shadow-root "+'rock-content-view'.upper())
    
    content_view_container=shadow_content_view.find_element(By.CSS_SELECTOR,'#content-view-container')
    #logger.info("Accessing to "+'content-view-container'.upper())
    
    shadow_container=content_view_container.find_element(By.CSS_SELECTOR,'app-entity-manage').shadow_root
    #logger.info("Activating shadow-root "+'app-entity-discovery'.upper())

    shadow_header=shadow_container.find_element(By.CSS_SELECTOR,'#entityManageHeader').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    shadow_actions=shadow_header.find_element(By.CSS_SELECTOR,'#entityActions').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    shadow_toolbar=shadow_actions.find_element(By.CSS_SELECTOR,'#toolbar').shadow_root
    #logger.info("Activating shadow-root "+'entityManageHeader'.upper())
    
    download_button=shadow_toolbar.find_element(By.CSS_SELECTOR,'pebble-button[title="Download File"]')
    logger.info(f"{download_button.text}")

    download_button.click()
    time.sleep(15)
    
    return driver

if __name__=='__main__':
    inicio=time.time()
    today=datetime.datetime.now()
    stamped_today=today.strftime("%Y-%m-%d")
    
    logger=logger_configuration(stamped_today)
    driver=driver_configuration(logger)
    driver=login(driver,logger)
    time.sleep(2)
    driver=goto_search(driver,logger)
    driver=check_all(driver,logger)
    driver=scroll_down(driver,logger)
    driver=download_button(driver,logger)
    driver=download_all(driver,logger)
    # TODO ==> Falta hacer esta funcion
    driver=wait_download(driver,logger)
    logger.info("=====> PROCESS COMPLETED <=====")
    driver.quit()

    