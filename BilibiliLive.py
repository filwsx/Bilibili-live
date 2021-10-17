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

#启动IDMan
def IDManStart(IDManSetDir):
    call([IDManSetDir])
         
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
    delayRandom(requestsMinTime, requestsMaxTime, 0.001)
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()  # 这里可能会抛出异常
        r.encoding = 'utf-8'
        response = [r.text,1]   #数组第二位为是否请求出错标志
    except :
        errorMessage = "【{}】请求出错".format(url)
        response = [errorMessage,0]
        logWrite("\n" + errorMessage)
    return response

class UPUP(object):
    def __init__(self, upID,rt):
        self.liveQuality = qualityLive
        self.mid = upID
        self.refreshTimes = rt
        self.live = {'name': '【未初始化】', 'roomid': '【未初始化】', 'title': '【未初始化】', 'status': 0, 'streamUrl': '【未初始化】'}  # status为直播状态，1为正在直播；streamUrl为直播流直链
        self.liveMessage = ""
        self.downloadDir = ""
        self.refreshParam()

    #数据初始化函数
    def refreshParam(self):
        mid = self.mid
        print('{}正在初始化基本信息'.format(mid))
        self.getUserInfo()
        self.downloadDir  = rootDir + self.live['name'] + "_"+ str(self.mid)
        if globalDownloadDir:
            self.downloadDir = globalDownloadDir
        makeDir(self.downloadDir)
        threading.Thread(target=self.liveDownload, daemon=True).start()
        threading.Thread(target=self.getDanmu, daemon=True).start()
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
            self.live['roomid'], self.liveQuality)
        r = downloadFile(url)
        if r[1]:
            response = json.loads(r[0])
            self.live['streamUrl'] = response['data']['durl'][0]['url']
        return self.live['streamUrl']
    
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
        try :
            while runFlag:
                DelayTime = random.randint(refreshLiveMinTime, refreshLiveMaxTime)
                nextTime = datetime.datetime.now() + datetime.timedelta(seconds=DelayTime)
                nextFreshTime = nextTime.strftime("%Y-%m-%d %H:%M:%S")
                self.liveMessage = "\n\t未开播：{}\n\t刷新次数：{}\n\t下次刷新：{}\n\t房间链接：https://live.bilibili.com/{}".format(upName, self.refreshTimes, nextFreshTime, roomId,)
                if self.getUserInfo():
                    streamUrl = self.getStreamUrl()
                    liveTitle = self.live['title']
                    liveFileName = datetime.datetime.now().strftime("{}_%Y-%m-%d_%H-%M-%S_{}.flv".format(upName,liveTitle))
                    self.liveMessage = "\n\tUP主：{}\n\t刷新次数：{}\n\t直播标题：{}\n\t房间链接：https://live.bilibili.com/{}\n\t下载链接：{}".format(upName, self.refreshTimes, liveTitle, roomId, streamUrl)
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
                            time.sleep(refreshLiveMaxTime)
                time.sleep(DelayTime)
        except Exception as ex:
            logWrite(ex)
            waitingSeconds(5)
            self.liveDownload()

#该函数实现了不同时段直播状态刷新频率不同，监视是否该结束脚本
def taskListening():
    global refreshLiveMinTime
    global refreshLiveMaxTime
    global runFlag
    global stopTime
    
    stopTime = 0    #是否设置截止时间
    changeFlage = 0 #是否设置分段刷新

    #初始化upTime为当前时间，使其满足currentTime > upTime来初始化正确值
    upTime = datetime.datetime.now()
    downTime = datetime.datetime.now()
    nowDate = datetime.datetime.now().strftime("%Y-%m-%d_")
    
    #设置不为空时，代表开启了定时关机
    if stopClockTime:
        stopTime = datetime.datetime.strptime(nowDate + stopClockTime,"%Y-%m-%d_%H-%M")
    #判断是否开启分段刷新
    if downClockTime and upClockTime:
        changeFlage = 1
    
    while runFlag:
        #分段和结束两个功能都未开启，此线程没必要继续运行了
        if not changeFlage and not stopTime:
            logWrite("分段与停滞两功能均未开启")
            break
        
        currentTime = datetime.datetime.now()
        
        #开启了定时关闭脚本
        if stopTime:
            #所有用户都没在直播（也就代表没有下载进程）且过了截止时刻
            if not len(liveOn) and currentTime > stopTime:
                runFlag = 0
        
        #开启分段刷新
        if changeFlage:
            #此判断用于解决7*24运行脚本带来的日期变更问题
            #之所以以upTime为变更临界点是因为upTime可能本身就是次日时间
            #以0点为临界点会造成0点-upTime这段时间失效
            if currentTime > upTime:
                nowDate = datetime.datetime.now().strftime("%Y-%m-%d_")
                downTime = datetime.datetime.strptime(nowDate + downClockTime,"%Y-%m-%d_%H-%M")
                upTime = datetime.datetime.strptime(nowDate + upClockTime,"%Y-%m-%d_%H-%M")
                #upTime为次日
                if upTime < downTime:
                    upTime = upTime + datetime.timedelta(days=1)
            
            if currentTime > downTime and currentTime < upTime:
                refreshLiveMinTime = setRefreshLiveMinTime
                refreshLiveMaxTime = setRefreshLiveMaxTime
            elif addNumber:
                refreshLiveMinTime = setRefreshLiveMinTime + addNumber
                refreshLiveMaxTime = setRefreshLiveMaxTime + addNumber
        
        time.sleep(10)


#线程：定时写入日志信息（主要是直播信息）
def LogListening(logTime):
    while runFlag:
        logWrite(allMessage)
        time.sleep(logTime)

#线程：为每个要监听的up创建一个对象，对象内有监听和下载线程
def liveListening(upIDlist):
    upObjectList = []
    global allMessage
    global runFlag
    global liveOn

    #开启各个up线程
    for i in upIDlist:
        liveVideo = UPUP(upID=i,rt = 0)
        upObjectList.append(liveVideo)
        waitingSeconds(5)
    
    #不断刷新屏幕信息
    while runFlag:
        liveOn = []  # 正在开播
        liveWaiting = []  # 等待开播
        liveMessage = "\n开播信息："
        for i in upObjectList:
            liveMessage = liveMessage + "\n" + i.liveMessage
            upName = i.live['name']
            if i.live['status']:
                liveOn.append(upName)
            else:
                liveWaiting.append(upName)
        
        liveStatusMessage = "\n开播状态：\n\t正在直播{}\n\t等待开播{}\n\t刷新间隔:{}到{}秒\n\t程序结束:{}".format(liveOn, liveWaiting, refreshLiveMinTime, refreshLiveMaxTime, stopTime)
        allMessage = liveStatusMessage + liveMessage
        if isWindows:
            os.system('cls')
        else:
            os.system('clear')
        print(allMessage)
        
        time.sleep(10)

if __name__ == '__main__':
    stopClockTime = "" #设置今日"23-30"截止时刻
    downClockTime = "18-30" #在每天downClockTime到upClockTime区间内高频率刷新直播状态
    upClockTime = "22-00"   #upClockTime小于downClockTime则默认为次日
    addNumber = 120        #设置空闲时间段刷新频率的加权值，值可正可负，不建议为负
    setRefreshLiveMinTime = 20  # 设置直播状态刷新随机间隔最小值，单位s
    setRefreshLiveMaxTime = 30  # 设置直播状态刷新随机间隔最大值，单位s
    requestsMinTime = 200  # 设置向B站请求时随机延时最小值，单位ms
    requestsMaxTime = 500  # 设置向B站请求时随机延时最大值，单位ms
    logFrequTime = 300   #日志写入频率，单位s

    qualityLive = 10000  # 设置直播流爬取质量:20000为4K,10000为原画,401为杜比蓝光,400为蓝光,250为超清,150为高清,80为流畅
    globalDownloadDir = ''  # 指定直播流的存储路径
    isAria2 = 1 # 是否用aria2下载直播流
    aria2cDir = r"aria2c"
    isIDM = 0  # 是否用IDM下载直播流，开启后请在下载前先启动IDM，否则程序处于阻塞状态
    IDM = r'C:\Program Files (x86)\Internet Download Manager\IDMan.exe'  # 指定IDM软件路径
    isBrowser = 0  # 是否用浏览器下载直播流
    
    runFlag = 1
    isWindows = 0
    logUUID = uuid.uuid1()
    rootDir = os.getcwd() + os.sep
    version = "BilibiliLiveBeta_V0.6.9"
    allMessage = "程序初始化完成\n程序版本：{}".format(version)
    
    if platform.system() == "Windows":
        isWindows = 1
        aria2cDir = r"{}aria2c.exe".format(rootDir)
        #IDMan.exe未运行则启动IDMan
        if not judgeprocess("IDMan.exe") and isIDM:
            threading.Thread(target=IDManStart, args=(IDM,), daemon=True).start()
    
    uplist = []  #要获取信息的UP主ID
    if len(sys.argv)>1:
        tempList = sys.argv[1].split(",")
    else:
        tempList = [398058064,163637592]
    for i in tempList :
        uplist.append(int(i))

    threadLog = threading.Thread(target=LogListening, args=(logFrequTime,), daemon=True)
    threadLive = threading.Thread(target=liveListening, args=(uplist,), daemon=True)
    threadChangeFre = threading.Thread(target=taskListening, daemon=True)
    threadList = [threadChangeFre,threadLog,threadLive]
    for i in threadList:
        i.start()
        
    while runFlag:
        time.sleep(100)
    allMessage = "程序即将结束\n程序版本：{}".format(version)
    logWrite(allMessage)
