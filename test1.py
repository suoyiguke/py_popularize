import json
import random
import time

import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

global noSet
noSet = set()

global list
list =[]

r = requests.get('http://192.168.100.201:8899/api/v1/proxies?limit=1000')
ip_ports = json.loads(r.text)['proxies']
for ip_object in ip_ports:
    ip_port = str(ip_object['ip']) + ':' + str(ip_object['port'])
    list.append(ip_port)



for ip in list:
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--proxy-server=http://' + ip)
    # chrome_options.add_argument('--proxy-server=http://111.164.177.131:8118')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    get = browser.get('http://www.baidu.com/')
    time.sleep(5)
    if get:
        print(get)
    else:
        browser.quit()



