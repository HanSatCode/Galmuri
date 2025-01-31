# -*- coding: utf-8 -*-

import os
import sys
from dirsync import sync
from tkinter import *
from win11toast import toast
from datetime import datetime

# Initial ───────────────────────────────────────────────────────────────
absPath = os.path.dirname(os.path.abspath(__file__))

path = open(f"{absPath}/Path.dat", 'r', encoding='UTF-8')
temp = path.readlines()
sourcePath = temp[0].rstrip()
targetPath = temp[1].rstrip()
path.close()

# Log ───────────────────────────────────────────────────────────────
def setMessageLog(description): # 설명 파라미터를 받아서 기록함
    log = open(f"{absPath}/log.txt", 'a', encoding='UTF-8')
    now = datetime.now()
    log.write(f"{now.strftime("%Y-%m-%d %H:%M:%S")} : {description}\n")
    return log.close()

# Core ───────────────────────────────────────────────────────────────
try:
    if os.listdir(targetPath) == []: # 새로운 폴더일경우
        sync(sourcePath, targetPath, 'sync')
        buttonPath = [
                {'activationType': 'protocol', 'arguments': f"{sourcePath}", 'content': "출발지 폴더"},
                {'activationType': 'protocol', 'arguments': f"{targetPath}", 'content': "목적지 폴더"}
        ]
        toast("갈무리 프로젝트", f"동기화가 완료되었습니다.\n출발지 혹은 목적지 폴더를 확인해보세요.", buttons = buttonPath)
    else:
        sync(sourcePath, targetPath, 'sync', purge=True, twoway=True)
        sync(targetPath, sourcePath, 'sync', purge=True, twoway=True)
        buttonPath = [
                {'activationType': 'protocol', 'arguments': f"{sourcePath}", 'content': "출발지 폴더"},
                {'activationType': 'protocol', 'arguments': f"{targetPath}", 'content': "목적지 폴더"}
        ]
        toast("갈무리 프로젝트", f"동기화가 완료되었습니다.\n출발지 혹은 목적지 폴더를 확인해보세요.", buttons = buttonPath)
except Exception as e:
        buttonPath = {'activationType': 'protocol', 'arguments': f"{absPath}\log.txt", 'content': "로그 열기"}
        toast("갈무리 프로젝트", f"동기화에 실패하였습니다.\n자세한 내용은 로그을 참조해주세요.", button = buttonPath)
        setMessageLog(f"[오류] '파일 동기화 중에 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        sys.exit()