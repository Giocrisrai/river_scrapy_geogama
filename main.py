import recaptcha.recaptcha_v2 as recaptcha
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time 
import pandas as pd
import os

def load_drive(website):
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')
    #options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" # Path to Brave Browser (this is the default)
    driver_path = '/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(options = options, executable_path = driver_path) 
    driver.get(website)
    
    return driver

def start_dga(driver):
    dga_data = driver.find_element_by_xpath('//*[@id="ing"]/div/table/tbody/tr/td/div/center[2]/font/input')
    dga_data.click()

def select_dropdown(name_river, driver):
    
    dropdown = Select(driver.find_element_by_xpath('//select[@name="estacion1"]'))
    dropdown.select_by_visible_text(name_river)
    
    look_parameter = driver.find_element_by_xpath('//*[@id="ing"]/div[3]/input')
    look_parameter.click()

def flow_click(flow, driver):
    flow = driver.find_element_by_xpath('//div[@class="dgarow"]//tr/td/input[@value='+'"'+flow+'"'+']')
    flow.click()

def start_date(driver):
    start = driver.find_element_by_xpath('//*[@id="fechaInicioTabla"]').click()
    
    start_month = driver.find_element_by_xpath('//*[@id="ing"]/div[7]/table[1]/tbody/tr[1]/td[2]/table/tbody/tr[5]/td[1]/div/div/div/p[1]/span[1]')
    month = 'Enero'
    for i in range(24):
        if month != driver.find_element_by_xpath('//*[@id="ing"]/div[7]/table[1]/tbody/tr[1]/td[2]/table/tbody/tr[5]/td[1]/div/div/div/p[1]/span[2]').text:
            start_month.click()
        else:
            break
    
    start_year = driver.find_element_by_xpath('//*[@id="ing"]/div[7]/table[1]/tbody/tr[1]/td[2]/table/tbody/tr[5]/td[1]/div/div/div/p[2]/span[1]')
    year = '2000'
    for i in range(24):
        if year != driver.find_element_by_xpath('//*[@id="year_name"]').text:
            start_year.click()
        else:
            break
        
    day = driver.find_elements_by_xpath('//div[@class="date_selector"]//tr/td[@class="selectable_day"]')
    for dateelement in day:
        date=dateelement.text
        if date =='1':
            dateelement.click()

def look_table(driver):
    table = driver.find_element_by_xpath('//*[@id="button22"]')
    table.click()

def save_data(driver):
    river_save = []
    
    pages = driver.find_element_by_xpath('//*[@id="titular"]/div/form/table[2]/tbody/tr[1]/td[2]')
    segmented_pages = pages.text.split()

    tour_page = int(segmented_pages[3])
    tour_page

    for i in range(tour_page):
        links = driver.find_elements_by_xpath('//*[@id="datos"]/tbody/tr')
        for link in links:
            river_save.append(link.text)
        next_page = driver.find_element_by_xpath('//*[@id="ava"]')
        next_page.click()
        
    return river_save

def config_river(name_river, flow,driver):
    start_dga(driver)
    select_dropdown(name_river, driver)
    flow_click(flow, driver)
    start_date(driver)
    time.sleep(10)

def solve_captcha(driver):
    url = driver.current_url

    g_response = recaptcha.solve_captcha(url)

    driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')

    driver.execute_script("""document.getElementById("g-recaptcha-response").innerHTML = arguments[0]""", g_response)
    driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="none";')

    # find iframe
    captcha_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.TAG_NAME, 'iframe'
            )
        )
    )

    ActionChains(driver).move_to_element(captcha_iframe).click().perform()
    
    # click im not robot
    captcha_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.ID, 'g-recaptcha-response'
            )
        )
    )

    driver.execute_script("arguments[0].click()", captcha_box)

    time.sleep(10)

    driver.find_element_by_xpath('//*[@id="button22"]').click()

def data_frame_river(river_transform, name_river_df):
    river = []
    data_origin = len(river_transform)
    for i in range(data_origin):
        river.append(river_transform[i].split())
        
    df = pd.DataFrame(river)
    df = df.drop([0], axis=1)
    df = df.rename(columns={1:'Fecha', 2:'Hora', 3:'caudal m3 '+name_river_df})
    
    return df

def config_river_data(website, name_river, flow_river, name):
    driver = load_drive(website)
    config_river(name_river, flow_river, driver)
    solve_captcha(driver)
    file_river = save_data(driver)
    df = data_frame_river(file_river, name)
    df.to_csv('rio_'+name+'.csv', index=False)

    driver.close()


if __name__ == '__main__':
    
    website = 'https://snia.mop.gob.cl/dgasat/pages/dgasat_main/dgasat_main.htm'
    
    river_chamiza = '10432002-3 Río Chamiza Ante Junta Río Chico'
    flow_chamiza = "10432002-3_12_Caudal (m3/seg)"
    config_river_data(website, river_chamiza, flow_chamiza, 'chamiza')

    river_puelo = '10523002-8 Río Puelo en Carrera Basilio'
    flow_puelo = "10523002-8_12_Caudal (m3/seg)"
    config_river_data(website, river_puelo, flow_puelo, 'puelo')

    river_fuetaleufu = '10704002-1 Río Futaleufu Ante Junta Río Malito'
    flow_futaleufu = "10704002-1_12_Caudal (m3/seg)"
    config_river_data(website, river_fuetaleufu, flow_futaleufu, 'futaleufu')

    river_palena = '11040001-2 Río Palena Bajo Junta Rosselot'
    flow_palena = "11040001-2_12_Caudal (m3/seg)"
    config_river_data(website, river_palena, flow_palena, 'palena')

    river_cisnes = '11147001-4 Río Cisnes en Puerto Cisnes'
    flow_cisnes = "11147001-4_12_Caudal (m3/seg)"
    config_river_data(website, river_cisnes, flow_cisnes, 'cisnes')

    river_aysen = '11342001-4 Río Aysen en Puerto Aysen'
    flow_aysen = "11342001-4_12_Caudal (m3/seg)"
    config_river_data(website, river_aysen, flow_aysen, 'aysen')

    river_exploradores = '11420000-K Río Exploradores en Nacimiento'
    flow_exploradores = "11420000-K_12_Caudal (m3/seg)"
    config_river_data(website, river_exploradores, flow_exploradores, 'exploradores')