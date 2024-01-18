import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import re
import csv

def find_sku_price(driver,url):
    driver.get(url)
    driver.implicitly_wait(3)
    try:
        sku = re.findall(r'sku\%22\%3A\%22(.+?)\%22\%2C\%22',driver.page_source)[0]
        if '%' in sku:
            sku = sku.split('%')[0]
    
    except:
        sku = None 
  
    return sku


def get_order_deails(driver,url,order):
    driver.get(url)
    driver.implicitly_wait(3)
    del order['order_details_url']
    order_details_page = driver.find_elements(By.CSS_SELECTOR, 'div[id="od-subtotals"]>div.a-row>div.a-column.a-span5.a-text-right.a-span-last')
    order['order_price'] = order_details_page[0].text
    order['delivery_cost'] = order_details_page[1].text
    order['tax'] = order_details_page[3].text
    products_details_section = driver.find_elements(By.CSS_SELECTOR,'div.a-fixed-right-grid.a-spacing-top-medium>div.a-fixed-right-grid-inner.a-grid-vertical-align.a-grid-top>div.a-fixed-right-grid-col.a-col-left>div.a-row  div.a-fixed-left-grid')
    length = len(products_details_section)
    for i in range (0,length):
            order[f'product_link_{i+1}'] = products_details_section[i].find_element(By.CSS_SELECTOR,'div.a-fixed-left-grid-inner div.a-fixed-left-grid-col.yohtmlc-item.a-col-right>div.a-row>a.a-link-normal').get_attribute('href')
            try:
                order[f'quantity_{i+1}'] = products_details_section[i].find_element(By.CSS_SELECTOR,'span.item-view-qty').text.strip()
            except:
                order[f'quantity_{i+1}'] = 1
            order[f'product_price_{i+1}'] = products_details_section[i].find_element(By.CSS_SELECTOR,'span.a-size-small.a-color-price').text.strip()    
    return order


def run_user(driver, username, password):
    driver.get('https://www.amazon.com')
    driver.implicitly_wait(2)
    time.sleep(5)

    if 'Hello, sign in' not in driver.page_source:
        driver.get("https://www.amazon.com/gp/css/homepage.html/ref=nav_bb_ya")


    try:
        login_check = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element(By.CSS_SELECTOR, 'div.nav-line-1-container>span.nav-line-1.nav-progressive-content'))).text
    except:
        login_check = "None"

    if login_check == 'Hello, sign in':
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'nav-tools'))).click()
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'ap_email'))).send_keys(username)
        time.sleep(1)
        print('Username Entered')
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'continue'))).click()
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'ap_password'))).send_keys(password)
        print('Password Entered')
        time.sleep(1)
        print("login Clicked")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'signInSubmit'))).click()
        try:
            submit_code = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'auth-mfa-otpcode')))
        except:
            submit_code = None
        if submit_code:
            print("in MFA code block")
            otp = input("Enter the code for 2FA: ")
            time.sleep(180)
            submit_code.send_keys(otp)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'auth-signin-button'))).click()

    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element('id', 'nav-orders'))).click()
    orders = []

    while True:
        items = driver.find_elements(By.CSS_SELECTOR, 'div.order-card.js-order-card')
        if len(items) < 1:
            print("No orders to scrap")
            return None
        for item in driver.find_elements(By.CSS_SELECTOR, 'div.order-card.js-order-card'):
            order = {}
            order['order_date'] = item.find_element(By.CSS_SELECTOR,'div.a-column.a-span4>div.a-row>span.a-size-base.a-color-secondary').text
            order['order_total'] = item.find_element(By.CSS_SELECTOR,'div.a-column.a-span2>div.a-row>span.a-size-base.a-color-secondary').text
            order['shipping_at'] = item.find_element(By.CSS_SELECTOR,'div.a-column.a-span6.a-span-last>div.yohtmlc-recipient>div.a-row.a-size-base').text
            order['order_id'] = item.find_element(By.CSS_SELECTOR,'div.a-box.a-color-offset-background.order-header div.a-fixed-right-grid-inner>div.a-text-right.a-fixed-right-grid-col.a-col-right>div.a-row.a-size-mini>div.yohtmlc-order-id').text.split(' ')[-1]
            order['order_details_url'] = item.find_element(By.CSS_SELECTOR,'div.yohtmlc-order-level-connections>a.a-link-normal').get_attribute('href')
            driver.implicitly_wait(3)
            orders.append(order)
            
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, 'ul.a-pagination li.a-last>a').get_attribute('href')
        except:
            next_page = None    
        if next_page:
            driver.get(next_page)
            continue
        else:
            break    
    
        
    
    final_orders = []
    for order in orders:
        order_details = get_order_deails(driver,order['order_details_url'],order)
        temp = {}
        for key,value in order_details.items():
            if 'product_link' in key:
                index = key.split('_')[-1]
                temp[f'sku_{index}'] = find_sku_price(driver, value)
        order_details.update(temp)
        print(order_details)
        final_orders.append(order_details)
    try:
        # logout
        driver.find_element('id','nav-item-signout').click()
        driver.close()
    except:
        driver.close()    
    
    return final_orders
    
    


if __name__ == '__main__':
    
    print('Creating session with Amazon website')
    chrome_options = Options()
    chrome_options.add_argument('log-level=3')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--allow-insecure-localhost")
    
    prefs = {
        'download.default_directory': "C:/",
        "directory_upgrade": True,
        "profile.default_content_settings.popups": 0,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    # initialise driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        with open('users.csv','r') as users_file:
            users = csv.DictReader(users_file,fieldnames=['username', 'password'])
            next(users)
            for user in users:
                orders = run_user(driver, user['username'], user['password'])
                if orders is not None:
                    with open(f"{user['username']}.csv",'a',newline='') as csv_file:
                        fieldnames = ['order_id','order_date','order_total','order_price','delivery_cost','tax','product_link_1','quantity_1','product_price_1','sku_1','product_link_2','quantity_2','product_price_2','sku_2','product_link_3','quantity_3','product_price_3','sku_3','product_link_4','quantity_4','product_price_4','sku_4','product_link_5','quantity_5','product_price_5','sku_5','product_link_6','quantity_6','product_price_6','sku_6','product_link_7','quantity_7','product_price_7','sku_7','product_link_8','quantity_8','product_price_8','sku_8','product_link_9','quantity_9','product_price_9','sku_9','product_link_10','quantity_10','product_price_10','sku_10','product_link_11','quantity_11','product_price_11','sku_11','product_link_12','quantity_12','product_price_12','sku_12']
                        writer = csv.DictWriter(csv_file, fieldnames=fieldnames,extrasaction='ignore',delimiter=';')
                        writer.writeheader()
                        for order in orders:
                            writer.writerow(order)
                else:
                    print(f"No orders for users {user['username']}")
    except:
        driver.close()
        driver.quit()
