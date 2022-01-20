import os
import psutil
import time

#检查一个进程是否存在，传入参数为该进程名字
def judgeprocess(processname):
   pl = psutil.pids()
   for pid in pl:
      if psutil.Process(pid).name() == processname:
          return True
   else:
     return False

if __name__ == '__main__':
    rootDir = os.getcwd() + os.sep
    cmd = r'.\\BilibiliStart.cmd'
    if not judgeprocess("cmd.exe"):
        os.system(cmd)
    #time.sleep(10)
