from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telegram

TEL_CHAT_ID = FILL_WITH_TELEGRAM_CHAT_ID
TEL_BOT_TOKEN = FILL_WITH_TELEGRAM_BOT_TOKEN
ALI_LOGIN_NAME = FILL_WITH_ALIEXPRESS_LOGIN_NAME
ALI_LOGIN_PASS = FILL_WITH_ALIEXPRESS_LOGIN_PASSWORD
WARNING_AT_DAYS = 5 #IF ORDER ENDS IN LESS THAN WARNING_AT_DAYS YOU WILL RECEIVE AN ALERT

text_file = open("Output.txt", "w", encoding="utf-8")

bot = telegram.Bot(token=TEL_BOT_TOKEN)
chrome_options = webdriver.ChromeOptions()  
#chrome_options.headless = True

driver = webdriver.Chrome("./chromedriver", chrome_options=chrome_options) 

driver.get("https://login.aliexpress.com/?returnUrl=https%3A%2F%2Ftrade.aliexpress.com%2ForderList.htm")

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fm-login-id")))


username = driver.find_element_by_id("fm-login-id")
username.send_keys(ALI_LOGIN_NAME)


password = driver.find_element_by_id("fm-login-password")
password.send_keys(ALI_LOGIN_PASS)

submit = driver.find_element_by_class_name("fm-submit")
submit.click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "remiandTips_waitBuyerAcceptGoods")))
submit = driver.find_element_by_id("remiandTips_waitBuyerAcceptGoods")
actions = ActionChains(driver)
actions.move_to_element(submit)
actions.click(submit)
actions.perform()
sleep(5)

text_file.write("Order ID;Product;Store;Value;Tracking ID;Carrier;Order time;Status\n")
orders = [["Order ID","Product(s)","Store","Value","Tracking ID","Carrier","Order Time","Status"]]

ordersleft = True
page=1
while ordersleft==True and page<=50:
    sleep(6)
    text_file.flush()
    order_elements = driver.find_elements_by_class_name("order-item-wraper")

    for x in order_elements:
        thisorder = [x.find_element_by_css_selector(".order-info .first-row .info-body").text,
        x.find_element_by_css_selector(".product-title .baobei-name").text,
        x.find_element_by_css_selector(".store-info .info-body").text,
        x.find_element_by_css_selector(".amount-num").text,"","",
        x.find_element_by_css_selector(".order-info .second-row .info-body").text,
        x.find_element_by_css_selector(".order-status .f-left").text]

        item = ";".join(str(z) for z in thisorder)
        if thisorder not in orders:
            print(item)
            text_file.write(item+"\n")

            orders.append(thisorder)
    
    nextbutton = driver.find_element_by_class_name("ui-pagination-next")

    if 'ui-pagination-disabled' in nextbutton.get_attribute('class').split():
        ordersleft = False
    else:
        nextbutton.click()
        page+=1
    
text_file.close()

text_file = open("Logistics.txt", "w", encoding="utf-8")

for y in orders:
    if y[7] == "Awaiting delivery":
        sleep(4)
        text_file.flush()
        driver.get("https://trade.aliexpress.com/order_detail.htm?orderId="+y[0])
        sleep(4)
        y[5] = driver.find_element_by_css_selector(".logistics-name").text
        y[4] = driver.find_element_by_css_selector(".logistics-num").text
        y[7] = driver.find_element_by_css_selector(".order-reminder").text
        x = re.search("([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))", y[7])
        
        d1 = datetime.now()
        d2 = datetime.strptime(x.group(1), "%Y-%m-%d")
        diff = abs((d2 - d1).days)
        if diff < 5:
                bot.send_message(chat_id=TEL_CHAT_ID, text="Only " + str(diff) + "days left " + "https://trade.aliexpress.com/order_detail.htm?orderId="+y[0])
        item = ";".join(str(z) for z in y)
        print(item)
        text_file.write(item+"\n")

text_file.close()
driver.quit()