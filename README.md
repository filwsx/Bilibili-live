# Bilibili-live
功能描述：用于挂机监听B站用户直播是否开播，开播则自动下载直播流(flv格式)和实时弹幕    

开发平台：windows10 + python3.9   

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
# 使用方法
1. 安装python并配置环境变量  
	python推荐版本3.9（因为开发用的这个版本，其他版本未经测试）
	
3. 下载工具配置  
    **windows平台**  
    下载[aria2c.exe](https://github.com/aria2/aria2/releases)，与py脚本放在同一目录下  
    或在代码中手动设置aria2c.exe绝对路径
    
    **ubuntu平台**  
    安装aria2   
    ```sudo snap install aria2c```  
    
4. json文件说明与配置
isopen用于控制是否爬取该用户，note为注释，down2up为快速刷新直播状态的时段，  
min2max为快速刷新时的随机时间取值范围，addTime+min到addTime+max为低频刷新时的取值范围  
qualityLive为直播画质:20000为4K,10000为原画,401为杜比蓝光,400为蓝光,250为超清,150为高清,80为流畅   
```json
{
    "sysConfig":
    [
     {"logFrequTime":300,"globalDownloadDir":"./live","isAria2":1,"aria2cDir":"./aria2c.exe","isBrowser":0}
    ],
    "user":
    [
        {"isOpen":1,"note":"罗翔说刑法","mid":517327498,"down2up":"18:30-22:00","addTime":120,"min2max":"20-30","qualityLive":10000},
        {"isOpen":0,"note":"我真的不懂分析","mid":85657899,"down2up":"18:30-22:00","addTime":120,"min2max":"20-30","qualityLive":10000}
    ]
}
```
4. 运行

   windows平台可直接运行BilibiliStart.cmd 

```shell
cd [脚本所在目录]
python BilibiliLive.py .\user.json
```

5. 关于稳定性

   因为未知原因，程序会异常终止。为避免监听中断，windows平台下可将BilibiliStart.cmd 设为开机和间隔1分钟运行
   

# 计划任务
- [ ] 存在未知原因的程序退出
- [x] 支持json配置程序其他参数
- [x] 增加浏览器与IDM下载支持
- [ ] ~~增加开播时间信息~~
- [x] 获得的直播标题可能存在非法字符
- [ ] ~~直播状态刷新调度器~~
- [ ] ~~直播对象监听与信息显示分开为两个线程~~

# 版本说明

在正式版本中删除了idm下载支持。如有需要参见 commit [0569a61](https://github.com/filwsx/Bilibili-live/commit/0569a611be024026839606a4015081e861c3b7e3) on 1 Nov 2021

简化了信息显示，可在自动生成的liveStatus.txt查看直播状态

[BilibiliLiveSimple.py](https://github.com/filwsx/Bilibili-live/blob/main/BilibiliLiveSimple.py)

	该本版仅支持windows平台下aria2下载，删去了日志输出和信息显示，要监听的主播保存在uplist列表内。
	直播流和弹幕下载功能与其他版本一致

# 参考资料

  https://blog.csdn.net/Enderman_xiaohei/article/details/102626855  
  https://blog.csdn.net/qq_43017750/article/details/107771744  

# 后记

  菜鸡写的代码，面向搜索引擎编程，结果是还能用，感觉还不错，分享给大家，欢迎指教  
