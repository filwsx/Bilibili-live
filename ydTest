#使用youtube-dl下载最高质量媒体，音视频分开。
#解决差网络环境导致的下载时常中断问题。
import youtube_dl
import os
import sys
import threading
import time

def waitingSeconds(sleepNumber):
    print("请等待{}s".format(sleepNumber))
    time.sleep(sleepNumber)

#对输出内容封装
def display(headline,content):
    print(headline)
    for i in content:
        print('\t',i)

#选择格式为质量最好的audio only和video only
#返回数据类型为数组
def getInfo(url):
    print('正在获取视频信息')
    try:
        info = youtube_dl.YoutubeDL().extract_info(url, download=False)
        r = info['formats']
        rv = {'filesize': 0,}
        ra = {'filesize': 0,}
        for i in r:
            videoInfo = i['vcodec']
            audioInfo = i['acodec']
            #仅含有音频
            if 'none' in videoInfo:
                #保存音频音质最好的,根据文件大小判断
                if i['filesize'] >= ra['filesize']:
                    ra = i
            #仅含有视频
            if 'none' in audioInfo:
                if i['filesize'] >= rv['filesize']:
                    rv = i
        #print(rv,ra)
        info['format'] = [rv,ra]
        return info
    except:
        #print('视频信息获取异常')
        waitingSeconds(5)
        info = getInfo(url)
        return info

class getStream(object):
    def __init__(self, mi, info):
        self.downloadFlag = 0
        self.errorTimes = 0
        self.ID = info['id']
        self.title = info['title']
        self.url = 'https://www.youtube.com/watch?v={}'.format(self.ID)
        self.mediaID = mi['format_id']
        self.mediaFormat = mi['format']
        threading.Thread(target=self.download, daemon=True).start()
        
    #下载视频监听钩子,下载完后将'downloadFlag'置1
    def statusHook(self,d):
        if d['status'] == 'finished':
           self.downloadFlag = 1
           #print('{}的{}格式下载完成'.format(self.title,self.mediaFormat))
    
    def download(self):
        self.errorTimes += 1
        #定义下载参数
        ydl_opts = {
            'format' : self.mediaID,
            'progress_hooks' : [self.statusHook],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print('{}的{}格式开始下载'.format(self.title,self.mediaFormat))
                result = ydl.download([self.url])
        except:
            print('下载出现异常')
            waitingSeconds(5)
            self.download()

if __name__ == '__main__':
    #因为网络环境或版权问题，设置脚本全局代理
    os.environ["http_proxy"] = "socks5://127.0.0.1:10808"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"
    
    #获取脚本参数
    if len(sys.argv)>1:
        tempList = sys.argv[1].split(",")
    else:
        tempList = ['https://www.youtube.com/watch?v=RKTRSZtrCLc']
    
    #创建下载对象
    upObjectList = []
    for i in tempList :
        info = getInfo(i)
        formatList = info['format']
        for j in formatList:
            getBestMedia = getStream(j,info)
            upObjectList.append(getBestMedia)
            waitingSeconds(5)
    
    #监听下载是否完成
    while True:
        doneNumber = 0
        done = []
        ing = []
        for i in upObjectList:
            doneNumber = doneNumber + i.downloadFlag
            if i.downloadFlag:
                done.append('{}的{}格式,出错次数{}'.format(i.title,i.mediaFormat,i.errorTimes-1))
            else:
                ing.append('{}的{}格式,出错次数{}'.format(i.title,i.mediaFormat,i.errorTimes-1))
        os.system('cls')
        display('已下载完：',done)
        display('正在下载：',ing)
        if doneNumber==len(upObjectList):
            print('已全部下载完成')
            break
        time.sleep(10)
