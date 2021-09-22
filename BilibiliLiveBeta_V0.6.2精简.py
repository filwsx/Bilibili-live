import datetime
import json
import os
import random
import time
from subprocess import call
import threading
import requests
def delayRandom(downTime, upTime, power):
    DelayTime = random.randint(downTime, upTime)
    time.sleep(DelayTime * power)
def downloadFile(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
    delayRandom(200, 500, 0.001)
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.encoding = 'utf-8'
        response = [r.text,1]   
    except :
        response = ["error",0]
    return response
class UPUP(object):
    def __init__(self, upID):
        self.liveQuality = 10000
        self.mid = upID
        self.crashFlag = 0  
        self.live = {'name': '【未初始化】', 'roomid': '【未初始化】', 'title': '【未初始化】', 'status': 0, 'streamUrl': '【未初始化】'}  
        self.downloadDir = ""
        self.refreshParam()
    def refreshParam(self):
        self.getUserInfo()
        self.downloadDir  = os.getcwd() + os.sep + self.live['name'] + "_"+ str(self.mid)
        if not os.path.exists(self.downloadDir):
            os.mkdir(self.downloadDir)
        threadLive = threading.Thread(target=self.liveDownload, daemon=True)
        threadDanmu = threading.Thread(target=self.getDanmu, daemon=True)
        threadLive.start()
        threadDanmu.start()
    def getUserInfo(self):
        url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(self.mid)
        r = downloadFile(url)
        if r[1]:
            response = json.loads(r[0])
            self.live['name'] = response['data']['name']
            self.live['roomid'] = response['data']['live_room']['roomid']
            self.live['title'] = response['data']['live_room']['title']
            self.live['status'] = response['data']['live_room']['liveStatus']
        return self.live['status']
    def getStreamUrl(self):
        url = 'https://api.live.bilibili.com/room/v1/Room/playUrl?cid={}&qn={}&platform=web'.format(self.live['roomid'], self.liveQuality)
        r = downloadFile(url)
        if r[1]:
            response = json.loads(r[0])
            self.live['streamUrl'] = response['data']['durl'][0]['url']
        return self.live['streamUrl']
    def getDanmu(self):
        DanmuURL = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory'
        DanmuHeaders = {'Host':'api.live.bilibili.com','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',}
        DanmuData = {'roomid':self.live['roomid'],'csrf_token':'','csrf':'','visit_id':'',}
        DanmuFileName = self.downloadDir + os.sep + datetime.datetime.now().strftime("{}_%Y-%m-%d.txt".format(self.live['name']))
        lines_seen = set()  
        while True:
            html = requests.post(url=DanmuURL,headers=DanmuHeaders,data=DanmuData).json()
            for content in html['data']['room']:
                nickname = content['nickname']  
                text = content['text']  
                timeline = content['timeline']  
                msg = timeline +' '+ nickname + ': ' + text + '\n'  
                if msg not in lines_seen:
                    lines_seen.add(msg)
                    with open(DanmuFileName,"a",encoding = 'utf-8') as logFile:
                        logFile.writelines(msg)
            if len(lines_seen)>1000:
                lines_seen.clear()
            time.sleep(2)
    def liveDownload(self):
        try :
            while True:
                if self.getUserInfo():
                    liveFileName = datetime.datetime.now().strftime("{}_%Y-%m-%d_%H-%M-%S_{}.flv".format(self.live['name'],self.live['title']))
                    call([aria2cDir, self.getStreamUrl(), '-d', self.downloadDir, '-o', liveFileName])
                    continue
                delayRandom(30, 50, 1)
        except Exception as ex:
            self.crashFlag = 1
def live(upIDlist):
    upObjectList = []
    for i in upIDlist:
        liveVideo = UPUP(upID=i)
        upObjectList.append(liveVideo)
    while True:
        liveOn = []  # 正在开播
        liveWaiting = []  # 等待开播
        for i in upObjectList:
            upName = i.live['name']
            if i.live['status']:
                liveOn.append(upName)
            else:
                liveWaiting.append(upName)
            if i.crashFlag:
                liveVideo = UPUP(upID=i.mid)
                upObjectList.remove(i)
                upObjectList.append(liveVideo)
        liveStatusMessage = "\n正在直播{}\n等待开播{}".format(liveOn, liveWaiting)
        os.system("cls")
        print(liveStatusMessage)
        time.sleep(5)
if __name__ == '__main__':
    aria2cDir = r"{}{}aria2c.exe".format(os.getcwd(),os.sep)
    uplist = [23191782,19147010,119801456,67738074,108142407,517327498]
    threading.Thread(target=live, args=(uplist,), daemon=True).start()
    while True:
        time.sleep(100)