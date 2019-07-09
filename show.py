import random
import requests

IPAgents = [
    "182.92.105.136:3128",
	]

try:
    requests.adapters.DEFAULT_RETRIES = 3
    IP = random.choice(IPAgents)
    thisProxy = "http://" + IP
    thisIP = "".join(IP.split(":")[0:1])
    #print(thisIP)
    res = requests.get(url="http://icanhazip.com/",timeout=8,proxies={"http":thisProxy})
    proxyIP = res.text.strip().replace("\n", "")
    if(thisProxy.find(proxyIP)!=-1):
        print("代理IP:'"+ proxyIP + "'有效！")
    else:
        print("代理IP无效！")
except:
    print("代理IP无效！")