"""
文件名：BilibiliLive.py
Beat_V0.1
    描述：本代码是在BilibiliAll_V0.6.2.py基础上精简，仅保留live监听功能的基础上而来。追求简单稳定。
    开始时间：20210910 0723
    结束时间：20210910 0927
V0.2
    增加了aria2下载功能
    V0.2.1与V0.2主要区别是aria2Listening()函数
    开始时间：20210910 1047
    结束时间：20210910 1409
V0.3.0
    aria2Listening()增加sleep，解决性能问题！
    20210910 1758
V0.4.0
    直播突然断播之后再上播，程序并未检测出来，要改进！
    之前想改进的方法正好可以解决此问题，1819开始
    同时为了方便实现我之前的功能，要重构代码逻辑，一个用户一个线程
    准备删除idm下载支持
    20210910 1758开始，1925完成初步，未测试
V0.4.1
    20210910 2036完成v0.4.0测试与修改，功能稳定
V0.4.2
    删除IDM下载支持
    删除delayLiveRefresh()与delayRequest()
    修复日志输出bug-没有直播信息输出
    20210910 2053完成
    在此基础上很好实现任务结束，自动关机：加个线程和检测标志（难点在这里）
v0.4.3
    增加自动关机功能
    20210911 0732左右想到，0745开始实现
    发现实现起来并不需要加任何标志，判断直播状态就好，0804基本完成，待测试
    0840放弃，语句并没有预期的作用，时间已经超过预期花费，果断放弃！
    0916完成，在我放弃没几分钟的时候想到了方法
    但是定时功能总觉得有问题，不令人放心（关闭后无消息提示等原因，一种不安），所以并不完美
v0.5.0
    20210911 2324开始
    v0.4.2实际运行发现有的监听线程并不刷新了，故进行更新
    觉得自己得系统的学习编程和设计模式、软件开发、数据结构和算法、操作系统。
    该版本未经测试，做出如下改动
    1.日志写入与日志监听分开
    2.为每个对象加入内部监听函数：如果出错则重新初始化对象。
    3.重写requests函数，因为怀疑就是这个原因代码崩掉了，请求频繁导致的出错从而线程崩了
    4.加入try结合日志写入来追踪问题，
    5.直播状态统一请求（放弃了）
    20210911 2333写完说明，开始实现。
    20210912 0026写完代码
v0.5.1
    20210912 0128测试完代码，没发现啥问题，就看长时间运行的稳定性了
    准备不关机，电脑运行一晚上看看
    0130睡觉去了！
v0.5.2
    20210912 0718写：发现新修改的版本更不稳定，因为重启线程本身就很随机不确定
    放弃v0.5.1中的监听把，想改为定时重新建立监听对象
    暂不实现，先测试删除新增功能后是否稳定
    20210912 0801让我想到了简单的方法，直接判断线程是否结束，我之前傻还是现在太聪明
v0.5.3
    20210912 0932修正了代码的问题，crashFlag并没能起作用，我猜想是因为遇到异常后线程直接挂掉，没能执行置1操作
    直接把while放到了try里。经测试，初始化完成后，禁用网络不刷新，但是回复网络后还可以正常刷新
    此程序就这样先跑一上午看看吧。0935写
v0.5.4
    对计数优化，保留上次崩溃时的刷新次数
    对崩溃信息进行日志输出
    1340实现完成，未测试，也用不到！
v0.5.5
    加入uuid标识每一次运行，多个运行区分日志信息
    20210912 1406完成
V0.5.6
    把日志输出文件统一放到runlog目录下，也包含了之前为了设定爬取用户方便加入的传参
    20210914 0839
V0.5.7
    20210915 0633开始，修改是文件名直播标题未更新的bug，0640完成
V0.5.8
    20210915 0655开始，进一步完善直播标题逻辑，主播期间可能会改标题，0701完成
V0.5.9
    20210918 1941:优化代码-删除直播刷新函数，因为和信息初始化高度重合；删除无用代码(request警告，视频文件名)；修订注释
V0.6.0
    20210919 2221开始增加直播弹幕获取功能
    20210919 2316测试完成
    20210919 2326加入去重代码，网上抄来的
V0.6.1
    改进弹幕保存，实时去重（主要是我怕内容太多数组炸列，影响效率，但是写入文件也很多，哎）
    20210919 2345完成，很快的！
V0.6.2
    增加了分时段刷新频率 20210922 1720左右开始，1758实现
    1858完成：测试分段刷新可用性，优化信息显示
V0.6.3
    将文件名改为BilibiliLiveBeta_V0.6.3
    beat和beta傻傻分不清楚20210922 2345
"""
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
    
