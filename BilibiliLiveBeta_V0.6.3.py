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

#power为0.001时为毫秒级延迟
def delayRandom(downTime, upTime, power):
    DelayTime = random.randint(downTime, upTime)
    time.sleep(DelayTime * power)

def makeDir(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

#往txt内增加日志信息
def logWrite(logMessage):
    global logUUID
    nowTime = datetime.datetime.now()
    logDir = os.getcwd() + dirChar + "runLog"
    makeDir(logDir)
    logFileName = logDir + dirChar + nowTime.strftime("runLog_%Y-%m-%d.txt")
    content = "\n日志时间：{}\n程序uuid：{}\n日志内容：{}\n".format(nowTime, logUUID, logMessage)
    with open(logFileName,"a",encoding = 'utf-8') as logFile:
        logFile.writelines(content)
    
#发出网络请求
def downloadFile(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}
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
        self.crashFlag = 0  #当该值置为1，代表liveDownload线程结束了
        self.live = {'name': '【未初始化】', 'roomid': '【未初始化】', 'title': '【未初始化】', 'status': 0, 'streamUrl': '【未初始化】'}  # status为直播状态，1为正在直播；streamUrl为直播流直链
        self.liveMessage = ""
        self.downloadDir = ""
        self.refreshParam()

    #数据初始化函数
    def refreshParam(self):
        mid = self.mid
        print('{}正在初始化基本信息'.format(mid))
        self.getUserInfo()
        self.downloadDir  = os.getcwd() + dirChar + self.live['name'] + "_"+ str(self.mid)
        if globalDownloadDir:
            self.downloadDir = globalDownloadDir
        makeDir(self.downloadDir)
        threading.Thread(target=self.liveDownload, daemon=True).start()
        threading.Thread(target=self.getDanmu, daemon=True).start()
        logMessage = '\n【{}初始化完成】'.format(mid)
        logWrite(logMessage)

    # 根据ID获取up基本信息，也是刷新直播状态
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
        DanmuHeaders = {'Host':'api.live.bilibili.com','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',}
        DanmuData = {'roomid':self.live['roomid'],'csrf_token':'','csrf':'','visit_id':'',}
        DanmuFileName = self.downloadDir + dirChar + datetime.datetime.now().strftime("{}_%Y-%m-%d.txt".format(self.live['name']))
        DanmuFileName = DanmuFileName.replace("\\\\", "\\")
        lines_seen = set()  #存储已写入弹幕信息用于去重
        global runFlag
        while runFlag:
            html = requests.post(url=DanmuURL,headers=DanmuHeaders,data=DanmuData).json()
            # 解析弹幕列表
            for content in html['data']['room']:
                nickname = content['nickname']  # 获取昵称
                text = content['text']  # 获取发言
                timeline = content['timeline']  # 获取发言时间
                msg = timeline +' '+ nickname + ': ' + text + '\n'  # 记录发言
                if msg not in lines_seen:
                    lines_seen.add(msg)
                    with open(DanmuFileName,"a",encoding = 'utf-8') as logFile:
                        logFile.writelines(msg)
            if len(lines_seen)>1000:
                lines_seen.clear()
            if self.live['status']:
                time.sleep(1)
            else:
                time.sleep(logFrequTime)

    #线程：监听当前对象直播
    def liveDownload(self):
        upName = self.live['name']
        roomId = self.live['roomid']
        global runFlag
        try :
            while runFlag:
                self.refreshTimes = self.refreshTimes + 1
                refreshTimes = self.refreshTimes
                onLive = self.getUserInfo()   #更新直播状态
                DelayTime = random.randint(refreshLiveMinTime, refreshLiveMaxTime)
                nextTime = datetime.datetime.now() + datetime.timedelta(seconds=DelayTime)
                nextFreshTime = nextTime.strftime("%Y-%m-%d %H:%M:%S")
                self.liveMessage = "\n\t未开播：{}\n\t刷新次数：{}\n\t下次刷新：{}\n\t房间链接：https://live.bilibili.com/{}".format(upName, refreshTimes, nextFreshTime, roomId,)
                if onLive:
                    streamUrl = self.getStreamUrl()
                    liveTitle = self.live['title']
                    liveFileName = datetime.datetime.now().strftime("{}_%Y-%m-%d_%H-%M-%S_{}.flv".format(upName,liveTitle))
                    self.liveMessage = "\n\tUP主：{}\n\t刷新次数：{}\n\t直播标题：{}\n\t房间链接：https://live.bilibili.com/{}\n\t下载链接：{}".format(upName, refreshTimes, liveTitle, roomId, streamUrl)
                    #下载线程会自己卡在这里，一直下载直到网络中断或者下播，这样不用记录是否下载，也不用对在直播up请求了
                    call([aria2cDir, streamUrl, '-d', self.downloadDir, '-o', liveFileName])
                    continue
                time.sleep(DelayTime)
        except Exception as ex:
            self.crashFlag = 1
            logWrite(ex)

#该函数实现了不同时段直播状态刷新频率不同
#cct为changeClockTime，意味过了这个时刻用设定频率刷新
#pcct为perCCT，cct之前刷新频率：baseFrequency[min，max]+pcct，单位s
def changeRequestFrequent(pcct,cct):
    global nowDate
    global runFlag
    global setRefreshLiveMinTime
    global refreshLiveMinTime
    global setRefreshLiveMaxTime
    global refreshLiveMaxTime
    refreshLiveMinTime = setRefreshLiveMinTime + pcct
    refreshLiveMaxTime = setRefreshLiveMaxTime + pcct
    if len(cct):
        changeTime = datetime.datetime.strptime(nowDate + cct,"%Y-%m-%d_%H-%M")
        while runFlag:
            currentTime = datetime.datetime.now()
            if currentTime > changeTime:
                refreshLiveMinTime = setRefreshLiveMinTime
                refreshLiveMaxTime = setRefreshLiveMaxTime
                logWrite("改变刷新频率")
                break;
    else:
        logWrite("未设定刷新时刻")


#线程：定时写入日志信息（主要是直播信息）
def runLog(logTime):
    global runFlag
    global allMessage
    while runFlag:
        logWrite(allMessage)
        time.sleep(logTime)

#线程：为每个要监听的up创建一个对象，对象内有监听和下载线程
def live(upIDlist):
    upObjectList = []
    global allMessage
    global stopTime
    global runFlag
    #开启各个up线程
    for i in upIDlist:
        liveVideo = UPUP(upID=i,rt = 0)
        upObjectList.append(liveVideo)
        print("请等待5s")
        time.sleep(5)
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
            
            #对已结束线程进行重新初始化
            if i.crashFlag:
                cfrt = i.refreshTimes
                liveVideo = UPUP(upID=i.mid,rt = cfrt)
                upObjectList.remove(i)
                upObjectList.append(liveVideo)
        liveStatusMessage = "\n开播状态：\n\t正在直播{}\n\t等待开播{}\n\t刷新频率:{}到{}秒\n\t程序结束:{}".format(liveOn, liveWaiting, refreshLiveMinTime, refreshLiveMaxTime, stopTime)
        allMessage = liveStatusMessage + liveMessage
        os.system("cls")
        print(allMessage)
        nowTime = datetime.datetime.now()
        #开启了定时关机设定
        if stopTime:
            #所有用户都没在直播（也就代表没有下载进程）且过了截止时刻
            if not len(liveOn) and nowTime > stopTime:
                runFlag = 0
        time.sleep(5)

if __name__ == '__main__':
    version = "BilibiliLiveBeta_V0.6.3"
    dirChar = os.sep
    runFlag = 1
    allMessage = "程序初始化完成\n程序版本：{}".format(version)
    logUUID = uuid.uuid1()
    stopClockTime = "" #设置今日"23-30"截止时刻
    changeClockTime = "16-00" #设置刷新频率的分隔时刻，该时刻前为空闲时刻，刷新频率低
    pcctNumber = 300    #设置空闲时间段刷新频率的加权值，值可正可负，不建议为负
    setRefreshLiveMinTime = 30  # 设置直播状态刷新随机间隔最小值，单位s
    setRefreshLiveMaxTime = 50  # 设置直播状态刷新随机间隔最大值，单位s
    requestsMinTime = 200  # 设置向B站请求时随机延时最小值，单位ms
    requestsMaxTime = 500  # 设置向B站请求时随机延时最大值，单位ms
    qualityLive = 10000  # 设置直播流爬取质量:20000为4K,10000为原画,401为杜比蓝光,400为蓝光,250为超清,150为高清,80为流畅
    aria2cDir = r"{}{}aria2c.exe".format(os.getcwd(),dirChar)
    globalDownloadDir = ''  # 指定IDM下载直播流的存储路径
    logFrequTime = 300   #日志写入频率，单位s
    uplist = []  #要获取信息的UP主ID
    if len(sys.argv)>1:
        tempList = sys.argv[1].split(",")
    else:
        tempList = []   #默认监听直播的ID
    for i in tempList :
        uplist.append(int(i))
    
    nowDate = datetime.datetime.now().strftime("%Y-%m-%d_")
    
    #设置不为空时，代表开启了定时关机
    if stopClockTime:
        stopTime = datetime.datetime.strptime(nowDate + stopClockTime,"%Y-%m-%d_%H-%M")
    else:
        stopTime = 0
    
    threadLog = threading.Thread(target=runLog, args=(logFrequTime,), daemon=True)
    threadLive = threading.Thread(target=live, args=(uplist,), daemon=True)
    threadChangeFre = threading.Thread(target=changeRequestFrequent, args=(pcctNumber,changeClockTime,), daemon=True)
    threadList = [threadChangeFre,threadLog,threadLive]
    for i in threadList:
        i.start()
        
    while runFlag:
        time.sleep(1)
    allMessage = "程序即将结束\n程序版本：{}".format(version)
    logWrite(allMessage)
    
