import datetime
import json
import os
import sys
import random
import time
from subprocess import call
import uuid
import threading
import requests
import platform
import psutil
import webbrowser
import re
def waitingSeconds(sleepNumber):
    print("请等待{}s".format(sleepNumber))
    time.sleep(sleepNumber)
#power为0.001时为毫秒级延迟
def delayRandom(downTime, upTime, power):
    DelayTime = random.randint(downTime, upTime)
    time.sleep(DelayTime * power)
def makeDir(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
#检查一个进程是否存在，传入参数为该进程名字
def judgeprocess(processname):
   pl = psutil.pids()
   for pid in pl:
      if psutil.Process(pid).name() == processname:
          return True
   else:
     return False
#往txt内增加日志信息
def logWrite(logMessage):
    nowTime = datetime.datetime.now()
    logDir = rootDir + "runLog" + os.sep
    makeDir(logDir)
    logFileName = logDir + nowTime.strftime("runLog_%Y-%m-%d.txt")
    content = "\n日志时间：{}\n程序uuid：{}\n日志内容：{}\n".format(nowTime, logUUID, logMessage)
    with open(logFileName,"a",encoding = 'utf-8') as logFile:
        logFile.writelines(content)
#发出网络请求
def downloadFile(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
    requestsMinTime = 200  # 设置向B站请求时随机延时最小值，单位ms
    requestsMaxTime = 500  # 设置向B站请求时随机延时最大值，单位ms
    delayRandom(requestsMinTime, requestsMaxTime, 0.001)
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()  # 这里可能会抛出异常
        r.encoding = 'utf-8'
        response = [r.text,1]   #数组第二位为是否请求出错标志
    except :
        requestErrorTimes += 1
        errorMessage = "【{}】请求出错".format(url)
        response = [errorMessage,0]
    return response
class UPUP(object):
    def __init__(self,upMessage):
        self.upMessage = upMessage
        self.live = {'name': '【未初始化】', 'roomid': '【未初始化】', 'title': '【未初始化】', 'status': 0, 'streamUrl': '【未初始化】'}  # status为直播状态，1为正在直播；streamUrl为直播流直链
        self.liveMessage = ""
        self.downloadDir = ""
        self.refreshTimes = 0
        self.tempNumber = 0
        self.mid = 398058064
        self.downTime = "18:30" #在每天downTime到upTime区间内高频率刷新直播状态
        self.upTime = "22:00"   #upTime小于downTime则默认为次日
        self.minTime = 20  # 设置直播状态刷新随机间隔最小值，单位s
        self.maxTime = 30  # 设置直播状态刷新随机间隔最大值，单位s
        self.addTime = 120        #设置空闲时间段刷新频率的加权值，值可正可负，不建议为负
        self.qualityLive = 10000  # 设置直播流爬取质量:20000为4K,10000为原画,401为杜比蓝光,400为蓝光,250为超清,150为高清,80为流畅
        self.refreshParam()
    #数据初始化函数
    def refreshParam(self):
        DATA = self.upMessage
        mid = DATA['mid']
        print('{}正在初始化基本信息'.format(mid))
        down2up = DATA['down2up'].split('-')
        min2max = DATA['min2max'].split('-')
        self.addTime = DATA['addTime']
        self.qualityLive  = DATA['qualityLive']
        self.mid = mid
        self.downTime= down2up[0]
        self.upTime= down2up[1]
        self.minTime = int(min2max[0])
        self.maxTime = int(min2max[1])
        self.getUserInfo()
        self.downloadDir  = rootDir + self.live['name'] + "_"+ str(self.mid)
        makeDir(self.downloadDir)
        threading.Thread(target=self.taskListening, daemon=True).start()
        threading.Thread(target=self.liveDownload, daemon=True).start()
        logMessage = '\n【{}初始化完成】'.format(mid)
        logWrite(logMessage)
    # 根据ID获取up基本信息，也是刷新直播状态
    def getUserInfo(self):
        self.refreshTimes = self.refreshTimes + 1
        url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(self.mid)
        r = downloadFile(url)
        if r[1]:
            response = json.loads(r[0])
            self.live['name'] = response['data']['name']
            self.live['roomid'] = response['data']['live_room']['roomid']
            self.live['title'] = response['data']['live_room']['title']
            self.live['status'] = response['data']['live_room']['liveStatus']
        return self.live['status']
    # 获取直播流url
    def getStreamUrl(self):
        url = 'https://api.live.bilibili.com/room/v1/Room/playUrl?cid={}&qn={}&platform=web'.format(
            self.live['roomid'], self.qualityLive)
        r = downloadFile(url)
        if r[1]:
            response = json.loads(r[0])
            self.live['streamUrl'] = response['data']['durl'][0]['url']
        return self.live['streamUrl']
    #该函数实现了不同时段直播状态刷新频率不同，监视是否该结束脚本
    def taskListening(self):
        changeFlage = 0 #是否设置分段刷新
        if self.downTime and self.upTime:
            changeFlage = 1
        while changeFlage:
            currentTime = datetime.datetime.now()
            nowDate = datetime.datetime.now().strftime("%Y-%m-%d_")
            downTime = datetime.datetime.strptime(nowDate + self.downTime,"%Y-%m-%d_%H:%M")
            upTime = datetime.datetime.strptime(nowDate + self.upTime,"%Y-%m-%d_%H:%M")
            #upTime为次日
            if upTime < downTime:
                upTime = upTime + datetime.timedelta(days=1)
            if currentTime > downTime and currentTime < upTime:
                self.tempNumber = 0
            else:
                self.tempNumber = self.addTime
            time.sleep(10)
    def getDanmu(self):
        DanmuURL = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory'
        DanmuData = {'roomid':self.live['roomid'],'csrf_token':'','csrf':'','visit_id':'',}
        DanmuHeaders = {'Host':'api.live.bilibili.com','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',}
        DanmuFileName = self.downloadDir + os.sep + datetime.datetime.now().strftime("{}_%Y-%m-%d.txt".format(self.live['name']))
        lines_seen = set()  #存储已写入弹幕信息用于去重
        try :
            while runFlag:
                html = requests.post(url=DanmuURL,headers=DanmuHeaders,data=DanmuData).json()
                # 解析弹幕列表
                for content in html['data']['room']:
                    msg = content['timeline'] +' '+ content['nickname'] + ': ' + content['text'] + '\n'  # 记录发言
                    if msg not in lines_seen:
                        lines_seen.add(msg)
                        with open(DanmuFileName,"a",encoding = 'utf-8') as logFile:
                            logFile.writelines(msg)
                if len(lines_seen)>1000:
                    lines_seen.clear()
                if self.live['status']:
                    time.sleep(3)
                else:
                    time.sleep(logFrequTime)
        except Exception as ex:
            logWrite(ex)
            self.getDanmu()
    #线程：监听当前对象直播
    def liveDownload(self):
        upName = self.live['name']
        roomId = self.live['roomid']
        roomURl = '房间链接：https://live.bilibili.com/{}'.format(roomId)
        try :
            while runFlag:
                DelayTime = random.randint(self.minTime+self.tempNumber, self.maxTime+self.tempNumber)
                nextTime = datetime.datetime.now() + datetime.timedelta(seconds=DelayTime)
                nextFreshTime = nextTime.strftime("%Y-%m-%d %H:%M:%S")
                self.liveMessage = "\n\t未开播：{}\n\t刷新次数：{}\n\t下次刷新：{}\n\t{}".format(upName, self.refreshTimes, nextFreshTime, roomURl)
                if self.getUserInfo():
                    streamUrl = self.getStreamUrl()
                    threading.Thread(target=self.getDanmu, daemon=True).start()
                    liveTitle = re.sub('[\/:*?"<>|]','_',self.live['title'])
                    liveFileName = datetime.datetime.now().strftime("{}_%Y-%m-%d_%H-%M-%S_{}.flv".format(upName,liveTitle))
                    self.liveMessage = "\n\tUP主：{}\n\t刷新次数：{}\n\t直播标题：{}\n\t{}\n\t下载链接：{}".format(upName, self.refreshTimes, liveTitle, roomURl, streamUrl)
                    #下载线程会自己卡在这里，一直下载直到网络中断或者下播，这样不用记录是否下载，也不用对在直播up请求了
                    if isBrowser:
                        webbrowser.open(streamUrl)
                    if isIDM and isWindows:
                        call([IDM, '/d', streamUrl, '/p', self.downloadDir, '/f', liveFileName, '/n'])
                    if isAria2:
                        call([aria2cDir, streamUrl, '-d', self.downloadDir, '-o', liveFileName])
                        waitingSeconds(5)    #防止aria2下载出错导致频繁请求
                        continue
                    else:#没有开启aria2下载就手动造成一个堵塞
                        while self.getUserInfo():#只要在直播就一直调用call下载
                            time.sleep(600)
                time.sleep(DelayTime)
        except Exception as ex:
            logWrite(ex)
            waitingSeconds(5)
            self.liveDownload()
#线程：定时写入日志信息（主要是直播信息）
def LogListening(logTime):
    while runFlag:
        logWrite(allMessage)
        time.sleep(logTime)
#线程：为每个要监听的up创建一个对象，对象内有监听和下载线程
def liveListening(upIDlist):
    upObjectList = []
    global allMessage
    #开启各个up线程
    for i in upIDlist:
        if i['isOpen']:
            liveVideo = UPUP(upMessage=i)
            upObjectList.append(liveVideo)
            waitingSeconds(5)
    #不断刷新屏幕信息
    while runFlag:
        liveOn = []  # 正在开播
        liveWaiting = []  # 等待开播
        liveMessage = "\n开播信息："
        for i in upObjectList:
            liveMessage += "\n" + i.liveMessage
            upName = i.live['name']
            if i.live['status']:
                liveOn.append(upName)
            else:
                liveWaiting.append(upName)
        liveStatusMessage = "\n开播状态：\n\t正在直播{}\n\t等待开播{}\n\t请求出错次数:{}".format(liveOn, liveWaiting, requestErrorTimes)
        allMessage = liveStatusMessage + liveMessage
        if isWindows:
            os.system('cls')
        else:
            os.system('clear')
        print(allMessage)
        time.sleep(10)
if __name__ == '__main__':
    logFrequTime = 300   #日志写入频率，单位s
    isAria2 = 1 # 是否用aria2下载直播流
    aria2cDir = r"aria2c"
    isIDM = 0  # 是否用IDM下载直播流，开启后请在下载前先启动IDM，否则程序处于阻塞状态
    IDM = r'C:\Program Files (x86)\Internet Download Manager\IDMan.exe'  # 指定IDM软件路径
    isBrowser = 0  # 是否用浏览器下载直播流
    runFlag = 1
    isWindows = 0
    requestErrorTimes = 0
    logUUID = uuid.uuid1()
    rootDir = os.getcwd() + os.sep
    version = "BilibiliLiveBeta_V0.7.2"
    allMessage = "程序初始化完成\n程序版本：{}".format(version)
    if platform.system() == "Windows":
        isWindows = 1
        aria2cDir = r".\aria2c.exe"
        #IDMan.exe未运行则启动IDMan
        if isIDM:
            if not judgeprocess("IDMan.exe"):
                threading.Thread(target=call, args=([IDM],), daemon=True).start()
    if len(sys.argv)>1:
        userFile = sys.argv[1]
        f = open(userFile,"r",encoding="utf-8") 
        data = json.load(f)
        uplist = data['user']
    else:
        uplist = []
    threadLog = threading.Thread(target=LogListening, args=(logFrequTime,), daemon=True)
    threadLive = threading.Thread(target=liveListening, args=(uplist,), daemon=True)
    threadList = [threadLog,threadLive]
    for i in threadList:
        i.start()
    while runFlag:
        time.sleep(100)
    allMessage = "程序即将结束\n程序版本：{}".format(version)
    logWrite(allMessage)
