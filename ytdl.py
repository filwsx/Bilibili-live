import youtube_dl
import os
import sys
import threading
import time
import re
from subprocess import call
def getAllFilePath(DIR,nameList):
    for i in os.listdir(DIR):
        i = os.path.join(DIR,i)
        if os.path.isdir(i):
            getAllFilePath(i,nameList)
        else:
            nameList.append(i)
    #print(nameList)
    return nameList
def getAllLine(filePath):
    data = []
    with open(filePath, "r", encoding='utf-8-sig') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line)>0:
                if line[0] != '#':
                    data.append(line)
    return data
def deleteExistFile(currentDir,filePath):
    allPath = []
    resultList = []
    allPath = getAllFilePath(currentDir,allPath)
    fileList = getAllLine(filePath)
    for j in fileList:
        findit = 0
        j = j.replace(cutChar,'')
        for i in allPath:
            if j in i:
                if not 'part' in i:
                    findit += 1
        #if findit<1:    #仅下载一个
        if findit<2:   #音视频均下载
            resultList.append(j)
    return resultList
def waitingSeconds(sleepNumber):
    print("请等待{}s".format(sleepNumber))
    time.sleep(sleepNumber)
def getInfo(url):
    try:
        info = youtube_dl.YoutubeDL().extract_info(url, download=False)
        r = info['formats']
        videoInfo = {'filesize': 0,}
        audioInfo = {'filesize': 0,}
        for i in r:
            vi = i['vcodec']
            ai = i['acodec']
            if 'none' in vi:
                if i['filesize'] >= audioInfo['filesize']:
                    audioInfo = i
            if 'none' in ai:
                if i['filesize'] >= videoInfo['filesize']:
                    videoInfo = i
        videoInfo['id'] = info['id']
        audioInfo['id'] = info['id']
        videoInfo['title'] = info['title']
        audioInfo['title'] = info['title']
        return [videoInfo,audioInfo]
    except:
        waitingSeconds(20)
        return getInfo(url)
class getStream(object):
    def __init__(self, info):
        self.downloadFlag = 0
        self.errorTimes = 0
        self.ID = info['id']
        self.title = info['title']
        self.url = '{}{}'.format(cutChar,self.ID)
        self.mediaID = info['format_id']
        self.mediaFormat = info['format']
        self.filSize = info['filesize']
        self.ext = info['ext']
        threading.Thread(target=self.downloadEXE, daemon=True).start()
        threading.Thread(target=self.doneListening, daemon=True).start()
    def statusHook(self,d):
        if d['status'] == 'finished':
           self.downloadFlag = 1
    def download(self):
        self.errorTimes += 1
        ydl_opts = {
            'format' : self.mediaID,
            'progress_hooks' : [self.statusHook],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([self.url])
        except:
            waitingSeconds(5)
            self.download()
    def doneListening(self):
        while True:
            try:
                allDir = []
                allDir = getAllFilePath(rootDir,allDir)
                if self.downloadFlag:
                    break
                pipei = '[{}] f{}.{}'.format(self.ID,self.mediaID,self.ext)
                for i in allDir:
                    if pipei in i:
                        if (pipei+'.part') in i:
                            self.downloadFlag = 0
                        else:
                            self.downloadFlag = 1
                        break
            except:
                pass
            time.sleep(5)
    def downloadEXE(self):
        while not self.downloadFlag:
            self.errorTimes += 1
            title = re.sub('[\/:*?"<>|]','_',self.title)
            fileName = './{} [{}] f{}.{}'.format(title,self.ID,self.mediaID,self.ext)
            call([ytdl, '-f', self.mediaID, '-o', fileName, self.url])
            waitingSeconds(5)
if __name__ == '__main__':
    proxyOn = 1
    maxNumber = 4   
    rootDir = os.getcwd()
    ytdl = './ytdl.exe'
    cutChar = 'https://www.youtube.com/watch?v='
    objectList = []
    objectDoneList = []
    objectHoldList = []
    if len(sys.argv)>2:
        proxyOn = sys.argv[1]
        objectHoldList = deleteExistFile(rootDir,sys.argv[2])
        #print(objectHoldList)
    if proxyOn:
        os.environ['http_proxy'] = 'socks5://127.0.0.1:10808'
        os.environ['https_proxy'] = 'http://127.0.0.1:10809'
    #while False:
    while True:
        for i in objectList:
            if i.downloadFlag:
                objectList.remove(i)
                objectDoneList.append(i)
        while len(objectList) < maxNumber and len(objectHoldList):
            urlID = objectHoldList[0]
            objectHoldList.remove(urlID)
            url = cutChar + urlID
            info = getInfo(url)
            for j in info:
                getBestMedia = getStream(j)
                objectList.append(getBestMedia)
                waitingSeconds(10)
        os.system('cls')
        fmt = '\t{:20}\t{:^10}\t{:^3}'
        print('已下载完数量：',len(objectDoneList))
        print('等待下载数量：',len(objectHoldList))
        print('正在下载：')
        print(fmt.format('标题','格式','出错次数'))
        for i in objectList:
            print(fmt.format(i.title[0:19],i.mediaFormat,i.errorTimes-1))
        if not len(objectList) and not len(objectHoldList):
            print('已全部下载完成')
            break
        time.sleep(10)
