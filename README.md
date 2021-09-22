# Bilibili-live
功能描述：用于挂机监听B站用户直播是否开播，开播则自动下载直播流和直播弹幕    
版本描述：精简版仅显示开播信息，删去了正常版本的各种显示信息和与核心功能无关的代码    
开发平台：windows10 + python3.9    
测试平台：windows10/Ubuntu20.04    

# 基本知识
up主的ID：    
  用户ID，纯数字。    
  以https://space.bilibili.com/163637592为例，网址最后一串数字为用户ID，请求参数中为mid。    
room_id：    
  即直播房间ID，纯数字。    
  以https://live.bilibili.com/5867219为例，网址最后一串数字为直播房间ID。    
请求数据格式均为json。    

# 开箱即用：
  **仅针对windows平台**
  安装python并配置环境变量    
  python推荐版本3.9（因为开发用的这个版本，其他版本未经测试）
  下载aria2c.exe，与py脚本放在同一目录下
  打开cmd 或 powershell执行
  '''
      cd [脚本所在目录]
      python [脚本文件名] [up主id]
  '''
  例如
  '''
  cd D:\test
  python BilibiliLiveBeta_V0.6.3.py 163637592,517327498,946974
  '''
# 程序配置
是否需要登录：不需要登陆

打开代码，跳转到'''python
  __name__ == '__main__'
  ''' 之后
  
必选：配置下载工具
  可使用：aria2/系统默认浏览器/idm
  默认使用与脚本同一目录下的aria2c.exe
  配置代码：
    aria2cDir = r"{}{}aria2c.exe".format(os.getcwd(),dirChar)

可选择功能1：设置脚本自动关闭时间
  配置代码：
    stopClockTime = "23-30" #设置今日"23：30"截止时刻
  说明：过了该时刻如果还有直播则不会停止脚本

可选择功能2：设置分段刷新频率
  由于不同时间段所关注的UP直播概率不同，为降低对服务器请求，在一些时间段降低请求频率
  该设置仅针对全局设置，不能针对某个用户个性化设置
  刷新间隔为某一区间内的随机数，单位s
  配置代码：
    changeClockTime = "16-00" #设置刷新频率的分隔时刻，默认该时刻前为空闲时刻，刷新频率低
    pcctNumber = 300    #设置空闲时间段刷新频率的加权值，单位s，可正可负
    #空闲时间刷新随机区间为/[min+pcctNumber,max+pcctNumber /]
    setRefreshLiveMinTime = 30  # 设置直播状态刷新随机间隔最小值，单位s
    setRefreshLiveMaxTime = 50  # 设置直播状态刷新随机间隔最大值，单位s
    
 可选择功能3：设置下载直播流画质
    qualityLive = 10000  # 设置直播流爬取质量:20000为4K,10000为原画,401为杜比蓝光,400为蓝光,250为超清,150为高清,80为流畅
    默认为最高画质
    
 可选择功能4：设置视频存储路径
    globalDownloadDir = ''  # 指定IDM下载直播流的存储路径
    默认路径为脚本所在目录，并为不同用户创建不同文件夹存储相关内容
    
 可选择功能5：设置运行日志写入频率
    logFrequTime = 300   #日志写入频率，单位s
    会在脚本所在目录创建runlog文件夹存储脚本日志，以天为单位
    
# 参考资料
  https://blog.csdn.net/Enderman_xiaohei/article/details/102626855
  https://blog.csdn.net/qq_43017750/article/details/107771744
  
# 计划任务
	- [ ] 增加开播时间信息
	- [ ] 获得的直播标题可能存在非法字符
	- [ ] 直播状态刷新调度器
  	- [ ] 直播对象监听与信息显示分开为两个线程

# 后记
  菜鸡写的代码，面向搜索引擎编程，结果是还能用，感觉还不错，分享给大家，欢迎指教
