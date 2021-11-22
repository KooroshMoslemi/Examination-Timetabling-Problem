import ctypes
from datetime import datetime
import sys
import time
import win32api
from collections import namedtuple
from pytz import timezone

TimeTuple = namedtuple("TimeTuple", "year month day hour minute second millisecond")
gams_tuple = TimeTuple(2014, 1, 1, 0, 0, 0, 0)
t1_tuple = None


def runAsAdmin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def isAdmin():
    return ctypes.windll.shell32.IsUserAnAdmin()


def setTime(time_tuple=gams_tuple, sync=False):
    global t1_tuple
    if not isAdmin():
        return

    if not sync:
        print("[+] Setting time...")
        now = datetime.now(timezone('UTC'))
        t1_tuple = TimeTuple(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond // 1000)
        dayOfWeek = datetime(*time_tuple).isocalendar()[2]
        win32api.SetSystemTime(*(time_tuple[:2] + (dayOfWeek,) + (time_tuple[2],) + t1_tuple[3:]))
        print("[+] Time is set")
    else:
        dayOfWeek = datetime(*time_tuple).isocalendar()[2]
        win32api.SetSystemTime(*(time_tuple[:2] + (dayOfWeek,) + time_tuple[2:]))


def syncTime():
    global t1_tuple
    if not isAdmin():
        return
    print("[+] Syncing time...")
    now = datetime.now(timezone('UTC'))
    t2_tuple = TimeTuple(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond // 1000)
    now_tuple = t1_tuple[:3] + t2_tuple[3:]
    setTime(now_tuple, True)
    print("[+] Time is synced!")


if __name__ == "__main__":
    #Testing Time Travel Module
    runAsAdmin()
    setTime()
    if isAdmin():
        time.sleep(5)
    syncTime()

