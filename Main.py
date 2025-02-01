# -*- coding: utf-8 -*-

import os
import sys
import threading
from winreg import *
from dirsync import sync
from tkinter import *
import tkinter.ttk
import tkinter.font
import tkinter.filedialog
import tkinter.messagebox
from win11toast import notify
from datetime import datetime


# Initialize ───────────────────────────────────────────────────────────────
absPath = os.path.dirname(os.path.abspath(__file__)) # 실행 환경마다 각각 다르기에, 절대 경로를 불러옴 (추후에 절대 경로 기준 사용 예정)

path = open(f"{absPath}/Path.dat", 'r', encoding='UTF-8') # Path.dat에 저장된 정보를 불러옴
temp = path.readlines()
sourcePath = temp[0].rstrip()
targetPath = temp[1].rstrip()
path.close()

config = open(f"{absPath}/Config.dat", 'r', encoding='UTF-8') # Config.dat에 저장된 정보를 불러옴 (다른 것으로 대체할 수 있지 않을까..?)
autoStatus = config.readline().rstrip()
config.close()


# Log Writer ───────────────────────────────────────────────────────────────
def setMessageLog(description): # 설명 파라미터를 받아서 기록함
    log = open(f"{absPath}/log.txt", 'a', encoding='UTF-8')
    now = datetime.now()
    log.write(f"{now.strftime("%Y-%m-%d %H:%M:%S")} : {description}\n")
    return log.close()


# GUI : Alert ───────────────────────────────────────────────────────────────

def setMessageBox(type, title, description):
    if type == "error":
        return tkinter.messagebox.showerror(title, description)
    elif type == "warning":
        return tkinter.messagebox.showwarning(title, description)
    else: # type == "info"
        return tkinter.messagebox.showinfo(title, description)


# Set Path ───────────────────────────────────────────────────────────────
def setSourcePath():
    try:
        global sourcePath # 상단에 있는 '전역변수 sourcePath' 또한 적용하기 위함
        tempSourcePath = tkinter.filedialog.askdirectory(title = "출발지 경로 선택")
        if tempSourcePath != "":
            sourcePath = tempSourcePath
            setMessageLog(f"[성공] 출발지 경로를 '{sourcePath}'(으)로 설정하였습니다.")
            entrySourcePath.config(state='normal')
            entrySourcePath.delete(0, tkinter.END)
            entrySourcePath.insert(0, sourcePath)
            entrySourcePath.config(state='readonly')
            return
        else: # 경로 재설정을 취소하는 경우
            setMessageLog(f"[성공] 출발지 경로 재설정을 취소하였습니다.")
            return
    except Exception as e:
        setMessageBox("error", "오류 발생", f"출발지 경로를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {print(e)}")
        setMessageLog(f"[오류] 출발지 경로를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {print(e)}")
        return sys.exit()

def setTargetPath():
    try:
        global targetPath
        tempTargetPath = tkinter.filedialog.askdirectory(title = "목적지 경로 선택")
        if tempTargetPath != "":
            targetPath = tempTargetPath
            setMessageLog(f"[성공] 목적지 경로를 '{targetPath}'(으)로 설정하였습니다.")
            entryTargetPath.config(state='normal')
            entryTargetPath.delete(0, tkinter.END)
            entryTargetPath.insert(0, targetPath)
            entryTargetPath.config(state='readonly')
            return
        else: # 경로 재설정을 취소하는 경우
            setMessageLog(f"[성공] 목적지 경로 재설정을 취소하였습니다.")
            return
    except Exception as e:
        setMessageBox("error", "오류 발생", f"목적지 경로를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        setMessageLog(f"[오류] 목적지 경로를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        return sys.exit()

def applyPath():
    try:
        if sourcePath == "" or targetPath == "": # 빈 공백
            setMessageBox('warning', "경로가 설정되지 않음", "출발지 경로 혹은 목적지 경로가 설정되지 않았습니다.")
            setMessageLog(f"[경고] 출발지 경로 혹은 목적지 경로가 설정되지 않았습니다.")
        elif sourcePath[-2:] == ':/' or targetPath[-2:] == ':/': # 파티션 별 루트 디렉토리는 접근 거부로 인해 설정 불가능
            setMessageBox("warning", "루트 디렉토리 설정 불가", "루트 디렉토리는 출발지 혹은 목적지 경로로 설정이 불가능합니다. 루트 디렉토리에 폴더를 생성하여 경로를 우회하거나, 다른 경로를 선택해주세요.")
            setMessageLog(f"[경고] 루트 디렉토리는 출발지 혹은 목적지 경로로 설정이 불가능합니다.")
        elif sourcePath == targetPath:
            setMessageBox("warning", "출발지 경로와 목적지 경로가 같음", "출발지 경로와 목적지 경로가 같습니다. 둘 중 하나는 다른 경로를 선택해주세요.")
            setMessageLog(f"[경고] 출발지 경로와 목적지 경로가 같습니다.")
        else:
            dat = open(f"{absPath}/Path.dat", 'w')
            dat.write(f"{sourcePath}\n{targetPath}")
            dat.close()
            setMessageBox("info", "경로 적용 완료", "출발지 및 목적지 경로를 정상적으로 적용하였습니다.")
            setMessageLog(f"[성공] 출발지 경로 '{sourcePath}' 목적지 경로 '{targetPath}'를 정상적으로 적용하였습니다.")
            return
    except Exception as e:
        setMessageBox("error", "오류 발생", f"출발지 및 목적지 경로를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        setMessageLog(f"[오류] '출발지 및 목적지 경로를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        return sys.exit()


# Sync ───────────────────────────────────────────────────────────────
def startSync():
    if sourcePath == '' or targetPath == '':
        setMessageBox("warning", "경로가 설정되지 않음", "출발지 경로 혹은 목적지 경로가 입력되지 않았습니다.")
        setMessageLog(f"[경고] 출발지 경로 혹은 목적지 경로가 입력되지 않았습니다.")
    else:
        root.title("갈무리 프로젝트 (동기화 중...)")
        syncCore(sourcePath, targetPath) # 코어 함수 사용. GUI의 데몬 스레드로 사용하진 않을 예정 (레이스 컨디션 예방)
        root.title("갈무리 프로젝트")
        return

def syncCount(sourcePath, targetPath):
    sourceList = set(os.listdir(sourcePath)) # 디렉토리의 파일 목록을 가져옴
    targetList = set(os.listdir(targetPath))
    common = sourceList.intersection(targetList) # 두 디렉토리에서 공통된 파일의 개수를 가져옴
    syncCnt = len(sourceList - common) + len(targetList - common) # 동기화할 파일의 개수를 계산함
    return syncCnt

def syncCore(sourcePath, targetPath):
    try:
        if os.listdir(targetPath) == []: # 새로운(빈) 폴더일 때
            sync(sourcePath, targetPath, 'sync')
            buttonPath = [
                {'activationType': 'protocol', 'arguments': f"{sourcePath}", 'content': "출발지 폴더"},
                {'activationType': 'protocol', 'arguments': f"{targetPath}", 'content': "목적지 폴더"}
            ]
            setMessageLog(f"[성공] 동기화가 완료되었습니다. {sourcePath} -> {targetPath}")
            return notify("갈무리 프로젝트", f"동기화가 완료되었습니다!\n출발지 혹은 목적지 폴더를 확인해보세요.", buttons = buttonPath)
        else:
            sync(sourcePath, targetPath, 'sync', purge=True, twoway=True)
            sync(targetPath, sourcePath, 'sync', purge=True, twoway=True)
            buttonPath = [
                {'activationType': 'protocol', 'arguments': f"{sourcePath}", 'content': "출발지 폴더"},
                {'activationType': 'protocol', 'arguments': f"{targetPath}", 'content': "목적지 폴더"}
            ]
            setMessageLog(f"[성공] 동기화가 완료되었습니다. {sourcePath} -> {targetPath}")
            return notify("갈무리 프로젝트", f"동기화가 완료되었습니다!\n출발지 혹은 목적지 폴더를 확인해보세요.", buttons = buttonPath)
    except Exception as e:
        setMessageBox("error", "오류 발생", f"파일 동기화 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        setMessageLog(f"[오류] 파일 동기화 중에 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        return sys.exit()


# Sync AutoSet ───────────────────────────────────────────────────────────────
def syncSet():
    try:
        if checkButtonValue_syncAuto.get() == 1: # 자동 동기화를 설정했을 경우
            reg = CreateKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce")
            SetValueEx(reg, "GalmuriAuto", 0, REG_SZ, f"\"{absPath}\\AutoSync.pyw\"")
            config = open(f"{absPath}/config.dat", 'w', encoding='UTF-8') #config 설정
            config.write('1')
            setMessageLog(f"[성공] 자동 동기화를 설정하였습니다.")
            return config.close()
        else: # 자동 동기화를 해제했을 경우
            reg = CreateKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce")
            DeleteValue(reg, "GalmuriAuto")
            config = open(f"{absPath}/config.dat", 'w', encoding='UTF-8')
            config.write('0')
            setMessageLog(f"[성공] 자동 동기화를 해제하였습니다.")
            return config.close()
    except Exception as e:
        setMessageBox("error", "오류 발생", f"자동 동기화를 설정하는 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        setMessageLog(f"[오류] 자동 동기화를 설정하는 중에 중에 예상치 못한 오류가 발생하였습니다. 프로그램을 종료합니다. : {e}")
        return sys.exit()


# GUI - Core ───────────────────────────────────────────────────────────────
root = tkinter.Tk()
root.title("갈무리 프로젝트")
envWidth = root.winfo_screenwidth()
envHeight = root.winfo_screenheight()
appWidth = 500
appHeight = 225
root.geometry(f"{appWidth}x{appHeight}+{int((envWidth / 2) - (appWidth / 2))}+{int((envHeight / 2) - (appHeight / 2))}")
root.resizable(False, False) # 창조절 제한하기
root.iconbitmap(f"{absPath}/src/galmuri.ico")
root.configure(bg="#ffffff")


# GUI - Initialize ───────────────────────────────────────────────────────────────
entryValue_sourcePath = tkinter.StringVar()
entryValue_targetPath = tkinter.StringVar()
entryValue_sourcePath.set(sourcePath)
entryValue_targetPath.set(targetPath)

checkButtonValue_syncAuto = tkinter.IntVar()
checkButtonValue_syncAuto.set(autoStatus)


# GUI - Font ───────────────────────────────────────────────────────────────
checkButtonFont = tkinter.font.Font(family="Pretendard", size=10)
labelFont = tkinter.font.Font(family="Pretendard", size=12, weight='bold')
entryFont = tkinter.font.Font(family="Pretendard", size=14)
buttonFont = tkinter.font.Font(family="Pretendard", size=12)


# GUI - Elements ───────────────────────────────────────────────────────────────
labelFrameSourcePath = tkinter.LabelFrame(root, text="출발지 경로", bd=0, 
                                          relief='solid', background='#ffffff', font=labelFont)
entrySourcePath = tkinter.Entry(labelFrameSourcePath, width=50, state='readonly', textvariable=entryValue_sourcePath,
                            relief='solid', borderwidth=1, background='#ffffff', font=entryFont)

labelFrameTargetPath = tkinter.LabelFrame(root, text="목적지 경로", bd=0,
                                          relief='solid', background='#ffffff', font=labelFont)
entryTargetPath = tkinter.Entry(labelFrameTargetPath, width=50, state='readonly', textvariable=entryValue_targetPath,
                            relief='solid', borderwidth=1, background='#ffffff', font=entryFont)

buttonSourcePath = tkinter.Button(root, text="출발지 선택", command=setSourcePath,
                                    width=10, height=3, relief='solid', overrelief='solid',
                                    bd=0, bg='#ffffff', fg="#000000",
                                    compound='bottom',
                                    font=buttonFont,
                                    activebackground='#ff295f', activeforeground='#ffffff')

buttonTargetPath = tkinter.Button(root, text="도착지 선택", command=setTargetPath,
                                    width=10, height=3, relief='solid', overrelief='solid',
                                    bd=0, bg='#ffffff', fg="#000000",
                                    compound='bottom',
                                    font=buttonFont,
                                    activebackground='#294dff', activeforeground='#ffffff')


buttonApplyPath = tkinter.Button(root, text="경로 적용", command=applyPath,
                                    width=10, height=3, relief='solid', overrelief='solid',
                                    bd=0, bg='#ffffff', fg="#000000",
                                    compound='bottom',
                                    font=buttonFont,
                                    activebackground='#26ed80', activeforeground='#ffffff')


buttonSyncStart = tkinter.Button(root, text="동기화 시작", command=startSync,
                                    width=10, height=3, relief='solid', overrelief='solid',
                                    bd=0, bg='#ffffff', fg="#000000",
                                    compound='bottom',
                                    font=buttonFont,
                                    activebackground='#ffac26', activeforeground='#ffffff')

checkButtonSyncAuto = tkinter.Checkbutton(root, text="Windows(을)를 시작할 때마다 자동으로 동기화",
                                            command=syncSet, variable=checkButtonValue_syncAuto,
                                            relief='solid', overrelief='solid',
                                            bd=0, bg='#ffffff', fg='#000000',
                                            compound='bottom',
                                            font=checkButtonFont,
                                            activebackground='#ffffff', activeforeground='#ffac26')


# GUI - Place ───────────────────────────────────────────────────────────────
labelFrameSourcePath.pack(side='top', padx=10, pady=5)
entrySourcePath.pack(side='left', padx=10, pady=5)
labelFrameTargetPath.pack(side='top', padx=10, pady=5)
entryTargetPath.pack(side='left', padx=10, pady=5)
checkButtonSyncAuto.pack(side='bottom', pady=5)

buttonSourcePath.pack(side='left', padx=15, pady=5)
buttonTargetPath.pack(side='left', padx=15, pady=5)
buttonSyncStart.pack(side='right', padx=15, pady=5)
buttonApplyPath.pack(side='right', padx=15, pady=5)


# GUI - Run ───────────────────────────────────────────────────────────────
root.mainloop()