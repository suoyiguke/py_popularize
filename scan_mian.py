# -*- coding: utf-8 -*-
import sys
import time
from threading import Thread, Lock

import requests
from cffi import lock
from selenium.webdriver.chrome.options import Options

import logger
from client.py_cli import ProxyFetcher

log = logger.logger()
sys.setrecursionlimit(1000000)
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

global IPAgents
IPAgents = []
global IPAgentsLen
IPAgentsLen = -1

global localList
localList = []
global historySet
historySet = set()

global linkSet
linkSet = set()

if 'scan_url' in os.environ and 'scan_access_token' in os.environ:
    access_token = os.environ['popularize_access_token']
    object['keyword'] = os.environ['popularize_keyword']
else:
    with open('./config.yml', 'r', encoding="utf-8") as f:
        ymlFile = yaml.load(f.read(), Loader=yaml.FullLoader)
        access_token = ymlFile['popularize_access_token']
        object['keyword'] = ymlFile['popularize_keyword']

# # 初始化机器人小丁
webhook = 'https://oapi.dingtalk.com/robot/send?access_token={access_token}'.format(access_token=access_token)  # 填写你自己创建的机器人
xiaoding = DingtalkChatbot(webhook)


def has_ym(url):
    if url.find('http') == -1:
        url = pageURL + url

    return url


def coverHttps(url):
    if url.find('http') == -1:
        url = "https://" + url

    return url


def _remove_duplicate(dict_list):
    seen = set()
    new_dict_list = []
    for dict in dict_list:
        t_dict = {'cur': dict['cur']}
        t_tup = tuple(t_dict.items())
        if t_tup not in seen:
            seen.add(t_tup)
            new_dict_list.append(dict)
    return new_dict_list


# 点击所有链接
def send_url_verification(url, browser):
    # # 只扫描自己的域名
    # if url.find(url) != -1:
    #     ym = coverHttps(url)
    #     browser.get(ym)
    #     aList = browser.find_elements_by_css_selector("a")
    #     for a in aList:
    #         if a.text.find('游戏攻略')!=-1:
    #             a.click()
    #             time.sleep(2)
    print("暂时没有实现点击所有网站链接！")


def checkIp(IP):
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        if IP.find('http') == -1:
            IP = "http://" + IP
        res = requests.get(url="http://icanhazip.com/", timeout=8, proxies={"http": IP})
        proxyIP = res.text.strip().replace("\n", "")
        if (IP.find(proxyIP) != -1):
            print("代理IP:'" + proxyIP + "'有效！")
            return True
        else:
            print("代理IP无效！")
            return False

    except:
        print("代理IP无效！")
        return False


# 获得代理ip
def getPxIp():
    for ip in IPAgents:
        if checkIp(ip):
            return ip


def initIP():
    args = dict(host='192.168.100.201', port=6379, password='root', db=0)
    # 这里`zhihu`的意思是，去和`zhihu`相关的代理ip校验队列中获取ip
    # 　这么做的原因是同一个代理IP对不同网站代理效果不同
    fetcher = ProxyFetcher('https', strategy='greedy', redis_args=args)
    # 获取可用代理列表
    print(fetcher.get_proxies())  # or print(fetcher.pool)
    IPAgents.extend(fetcher.get_proxies())


def getBrowser():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--proxy-server=' + getPxIp())
    try:
        browser = webdriver.Remote(
            command_executor="http://chrome-scan:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
            options=chrome_options
        )
    except BaseException as err:
        log.error(err)
        browser = webdriver.Chrome(chrome_options=chrome_options)

    finally:
        log.error('请检查好Chrome环境！')

    return browser


def sendDingDing(bl, keyword):
    if bl:
        # print('检测到关键词: “' + keyword + '”在百度的第' + object['page'] + '页,第' + object['article '] + '条')
        xiaoding.send_text(msg='检测到关键词: “' + keyword + '”在百度的第'+ object['page'] +'页,第'+object['article ']+'条')
    else:
        # print('检测到关键词: “' + keyword + '”没有被百度收录')
        xiaoding.send_text(msg='检测到关键词: “' + keyword + '”没有被百度收录')


def threadSend(url,keyword):
    if 'page' not in object:
        browser = getBrowser()
        time.sleep(2)
        browser.get('https://www.baidu.com/')
        time.sleep(1)
        try:
            selector = browser.find_element_by_css_selector('#kw')
            selector.send_keys(keyword)
            time.sleep(1)
            browser.find_element_by_css_selector('#su').click()
            time.sleep(1)
            resolution_page(url,browser.page_source, browser,keyword)

        except BaseException as err:
            browser.quit()
            log.error(err)
            threadSend(url,keyword)

        browser.quit()


def resolution_page(url,text, browser,keyword):
    soup = BeautifulSoup(text, 'lxml')
    selects = soup.select("div[class='result c-container']")
    i = 0
    for div in selects:

        i += 1
        aList = div.select("a[class='c-showurl']")
        for a_ in aList:
            if a_.text.find(url) != -1:
                print('找到了！')
                page = soup.select_one("span[class='fk fk_cur']").find_next_sibling().text
                print('第' + page + '页')
                print('第' + str(i) + '条')
                lock.acquire()
                object['page'] = soup.select_one("span[class='fk fk_cur']").find_next_sibling().text
                object['article '] = str(i)
                lock.release()

                # 推送订订消息
                sendDingDing(True, keyword)

                # 点击进入官网
                num = (int(page) - 1) * 10 + i
                browser.find_element_by_id(str(num)).find_element_by_css_selector("a").click()
                time.sleep(2)
                send_url_verification(url, browser)

                break
        else:
            continue
        break

    # 没找到就点击下一页继续
    else:
        print('下一页....')

        selectors = browser.find_elements_by_css_selector('.n')
        flag = True
        for selector_ in selectors:
            if selector_.text.find('下一页') != -1:
                flag = False
                time.sleep(1)
                selector_.click()
                time.sleep(1)
                resolution_page(url,browser.page_source, browser,keyword)

        #没有下一页了，就是没找到
        # 推送订订消息
        if flag:
            sendDingDing(False, keyword)


def main():
    # 初始化ip
    # initIP();
    log.debug('=================扫描程序开始==========================')
    # 线程list
    threads = []
    keywordList = object['keyword'].split("|")

    for keyword in keywordList:
        aList = keyword.split("=")
        bList = aList[len(aList)-1].split(",")
        for bKey in bList:
            p = Thread(target=threadSend, args=(aList[0],bKey))
            p.start()
            threads.append(p)

    for t in threads:
        t.join()

    log.debug('=================扫描程序结束==========================')


if __name__ == '__main__':
    main()
