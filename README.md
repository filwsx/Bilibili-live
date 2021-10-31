# ydTest
使用youtube-dl下载最高质量媒体，音视频分开。  
解决差网络环境导致的下载时常中断问题。  

# Bilibili-live
功能描述：用于挂机监听B站用户直播是否开播，开播则自动下载直播流和直播弹幕    
版本描述：精简版仅显示开播信息，删去了正常版本的各种显示信息和与核心功能无关的代码    
开发平台：windows10 + python3.9   
python库：psutil  
测试平台：windows10/Ubuntu20.04    
是否需要登录：不需要登陆  
# 基本知识  
## mid：  
	即用户ID，纯数字。  
	以https://space.bilibili.com/163637592为例，网址最后一串数字163637592为用户ID。
## room_id：  
	即直播房间ID，纯数字。  
	以https://live.bilibili.com/5867219为例，网址最后一串数字5867219为直播房间ID。  
请求数据格式均为json。
# 使用方法（aria2下载）
1. 安装python并配置环境变量【已安装可跳过】  
	python推荐版本3.9（因为开发用的这个版本，其他版本未经测试）
2. 安装库  
   ``` pip install psutil```
3. 下载工具配置
    **windows平台**  
    下载[aria2c.exe](https://github.com/aria2/aria2/releases)，与py脚本放在同一目录下  
    或在代码中手动设置aria2c.exe绝对路径
    
    **ubuntu平台**  
    安装aria2 【已安装可跳过】  
    ```sudo snap install aria2c```  
4. json文件说明  
isopen用于控制是否爬取该用户，note为注释，down2up为快速刷新直播状态的时段，  
min2max为快速刷新时的随机时间取值范围，addTime+min到addTime+max为低频刷新时的取值
qualityLive为直播画质:20000为4K,10000为原画,401为杜比蓝光,400为蓝光,250为超清,150为高清,80为流畅   
```
{
    "user":
    [
        {"isOpen":1,"note":"罗翔说刑法","mid":517327498,"down2up":"18:30-22:00","addTime":120,"min2max":"20-30","qualityLive":10000},
        {"isOpen":0,"note":"我真的不懂分析","mid":85657899,"down2up":"18:30-22:00","addTime":120,"min2max":"20-30","qualityLive":10000}
    ]
}
```
5. 打开cmd、powershell或终端执行  
```
cd [脚本所在目录]
python3 [脚本文件名] [用户配置文件，utf-8编码]
#例如  
cd D:\test
python BilibiliLive.py .\user.json
```

# 程序配置
打开代码，跳转到```__name__ == '__main__'```之后  
## 必选：配置下载工具  
可使用：aria2/系统默认浏览器/idm  
默认使用aria2下载
配置代码：
```
    isAria2 = 1 # 是否启用aria2下载直播流
    aria2cDir = r"aria2c" # 指定aria2路径
    isIDM = 0  # 是否启用IDM下载直播流
    IDM = r'C:\Program Files (x86)\Internet Download Manager\IDMan.exe'  # 指定IDM软件路径
    isBrowser = 0  # 是否启用系统默认浏览器打开直播流链接
```  
# 参考资料  
  https://blog.csdn.net/Enderman_xiaohei/article/details/102626855  
  https://blog.csdn.net/qq_43017750/article/details/107771744  
# 计划任务
- [x] 增加浏览器与IDM下载支持
- [ ] 增加开播时间信息
- [x] 获得的直播标题可能存在非法字符
- [ ] 直播状态刷新调度器
- [ ] 直播对象监听与信息显示分开为两个线程
# 后记
  菜鸡写的代码，面向搜索引擎编程，结果是还能用，感觉还不错，分享给大家，欢迎指教  
