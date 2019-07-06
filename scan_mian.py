# -*- coding: utf-8 -*-
import sys
import time
from threading import Thread, Lock

from apscheduler.schedulers.blocking import BlockingScheduler
from cffi import lock
from gerapy.spiders import json

import logger
log = logger.logger()
log.debug('=================扫描程序开始==========================')
sys.setrecursionlimit(1000000)
import requests
import yaml
from bs4 import BeautifulSoup
from dingtalkchatbot.chatbot import DingtalkChatbot
from gevent import os
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

global pageURL
global xiaoding
global ymlFile
global access_token
global object
object = {}
lock = Lock()

if 'scan_url' in os.environ and  'scan_access_token' in os.environ:
    pageURL = os.environ['popularize_url']
    access_token = os.environ['popularize_access_token']
    object['keyword']  = os.environ['popularize_keyword']
else:
    with open('./config.yml', 'r', encoding="utf-8") as f:
        ymlFile = yaml.load(f.read(), Loader=yaml.FullLoader)
        pageURL = ymlFile['popularize_url']
        access_token = ymlFile['popularize_access_token']
        object['keyword']  = ymlFile['popularize_keyword']

# # 初始化机器人小丁
webhook = 'https://oapi.dingtalk.com/robot/send?access_token={access_token}'.format(access_token=access_token)  # 填写你自己创建的机器人
xiaoding = DingtalkChatbot(webhook)




# def click_sulu():
#     browser


# #获得代理ip
# def getPxIp():
#     r = requests.get('http://127.0.0.1:8000/')
#     ip_ports = json.loads(r.text)
#     randint_ = ip_ports[random.randint(0, len(ip_ports))]
#     ip_port = str(randint_[0]) + ':' + str(randint_[1])
#     return ip_port

def getBrowser():
    try:
        browser = webdriver.Remote(
            command_executor="http://chrome-scan:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME
        )
    except BaseException as err:
        log.error(err)
        browser = webdriver.Chrome()

    finally:
        log.error('请检查好Chrome环境！')

    return  browser

def sendDingDing(bl,keyword):
    if bl:
       print('检测到关键词: “' + keyword + '”在百度的第'+ object['page'] +'页,第'+object['article ']+'条')
       # xiaoding.send_text(msg='检测到关键词: “' + keyword + '”在百度的第'+ object['page'] +'页,第'+object['article ']+'条')
    else:
       print('检测到关键词: “' + keyword + '”没有被百度收录')
       # xiaoding.send_text(msg='检测到关键词: “' + keyword + '”没有被百度收录')

def threadSend(keyword,):
    browser = getBrowser()
    browser.get('https://www.baidu.com/')
    selector = browser.find_element_by_css_selector('#kw')
    selector.send_keys(keyword)
    time.sleep(1)
    browser.find_element_by_css_selector('#su').click()
    time.sleep(1)
    resolution_page(browser.page_source, browser)
    selectors = browser.find_elements_by_css_selector('.n')
    if len(selectors) == 0 or selectors[0].text.find('下一页') == -1:
        print('没找到！')
        sendDingDing(False,keyword)
    else:
        sendDingDing(True,keyword)
    browser.quit()

def resolution_page(text,browser):
    soup = BeautifulSoup(text, 'lxml')
    selects = soup.select("div[class='result c-container']")
    i = 0
    for div in selects:

        i+=1
        aList = div.select("a[class='c-showurl']")
        for a_ in aList:
            if a_.text.find(pageURL) != -1:
                print('找到了！')
                print('第'+soup.select_one("span[class='fk fk_cur']").find_next_sibling().text+'页')
                print('第'+str(i)+'条')
                lock.acquire()
                object['page'] = soup.select_one("span[class='fk fk_cur']").find_next_sibling().text
                object['article '] = str(i)
                lock.release()
                break
        else:
            continue
        break

    #没找到就点击下一页继续
    else:
        print('下一页....')
        selectors = browser.find_elements_by_css_selector('.n')
        for selector_ in selectors:
            if selector_.text.find('下一页') != -1:
                time.sleep(1)
                selector_.click()
                time.sleep(1)
                resolution_page(browser.page_source,browser)




def main():
    # 线程list
    threads = []
    keywordList = object['keyword'].split(",")

    for keyword in keywordList:
        p = Thread(target=threadSend, args=(keyword,))
        p.start()
        threads.append(p)

    for t in threads:
        t.join()



if __name__ == '__main__':
    main()

