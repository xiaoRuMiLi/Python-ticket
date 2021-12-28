# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-09-09 19:41:59
# @Last Modified by:   Marte
# @Last Modified time: 2021-09-13 20:26:51
#-*- coding: utf-8 -*-  ##设置编码方式
#QQ496631085

import win32clipboard as w #剪贴板
import win32api,win32gui,win32con,time
import sys
print(sys.version)
def setText(aString):
    """设置剪贴板文本"""
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_UNICODETEXT, aString)
    w.CloseClipboard()

def getText():
    """获取剪贴板文本"""
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_UNICODETEXT)
    w.CloseClipboard()
    return d

def send_Mess(hwnd):
    win32gui.PostMessage(hwnd,win32con.WM_PASTE, 0, 0)  # 向窗口发送剪贴板内容(粘贴) QQ测试可以正常发送
    time.sleep(0.3)
    win32gui.PostMessage(hwnd,win32con.WM_KEYDOWN,win32con.VK_CONTROL,0)  #  向窗口发送 回车键
    time.sleep(0.3)
    win32gui.PostMessage(hwnd,win32con.WM_KEYDOWN,win32con.VK_RETURN,0)  #  向窗口发送 回车键


    time.sleep(0.3)
    win32gui.PostMessage(hwnd,win32con.WM_KEYUP,win32con.VK_RETURN,0)
    time.sleep(0.3)
    win32gui.PostMessage(hwnd,win32con.WM_KEYUP,win32con.VK_CONTROL,0)
def send_qq_msg( hwnd, text):

    print('找到%s'%windowtitle)
    left,top,right,bottom = win32gui.GetWindowRect(hwnd)#窗口获取坐标
    print(left,top,right,bottom)
    print('窗口尺寸',right-left,bottom-top)

    setText('这是我要发送的内容')
    time.sleep(6)
    send_Mess(hwnd)

    win32gui.SetForegroundWindow(hwnd)# 指定句柄设置为前台，也就是激活

    win32gui.MoveWindow(hwnd,20,20,405,756,True)#改变窗口大小

    time.sleep(6)
    win32gui.SetBkMode(hwnd, win32con.TRANSPARENT)# 设置为后台
    time.sleep(1)
    #
    # 获取鼠标当前位置的坐标
    print(win32api.GetCursorPos())
    # 将鼠标移动到坐标处
    win32api.SetCursorPos((210, 747))
    # 左点击
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 210, 747, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 210, 747, 0, 0)
def click_mouse( x, y, sleep = 1):
     # 获取鼠标当前位置的坐标
    print(win32api.GetCursorPos())
    # 将鼠标移动到坐标处
    win32api.SetCursorPos((x, y))
    # 左点击
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(sleep)
def find_window(class_name, title):
    windowtitle = title  #窗口名
    hwnd = win32gui.FindWindow(class_name, windowtitle)
    if hwnd > 0:
        print('找到%s'%windowtitle)
        return hwnd
    else:
        print('没找到%s'%windowtitle)
        return 0


def get_all_hwnd(hwnd,mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})

def click_double_key( key1 = 65, key2=17, sleep=1):
    # 组合键输入ctrl+A
    # 注意：先按下的要后抬起
    win32api.keybd_event(key2,0,0,0) #ctrl按下
    win32api.keybd_event(key1,0,0,0) #a按下
    time.sleep(sleep)
    win32api.keybd_event(key1,0,0,0) #a抬起
    win32api.keybd_event(key2,0,0,0) #ctrl抬起
def click_key(key, sleep=0.5):
    # 单个按键
    # 注意：HOME键按下要抬起
    win32api.keybd_event(key,0,0,0)
    win32api.keybd_event(key,0,win32con.KEYEVENTF_KEYUP,0)
    time.sleep(sleep)
def input_number_by_key(keys, sleep=0.5):
    number = {
    '0': 96,
    '1': 97,
    '2': 98,
    '3': 99,
    '4': 100,
    '5': 101,
    '6': 102,
    '7': 103,
    '8': 104,
    '9': 105
    }
    for i in keys:
        click_key(number[i],sleep)

# import win32gui
hwnd_title = dict()
win32gui.EnumWindows(get_all_hwnd, 0)

# win32api.MessageBox(win32con.NULL, 'Python 你好！', '你好', win32con.MB_OK)
for h,t in hwnd_title.items():
    if t != "":
        print(h, t)
# #点击窗口button
# w=win32ui.FindWindow(None,windowtitle)
# b=w.GetDlgItem(窗口id)
# b.postMessage(win32con.BM_CLICK)
#
# 买入股票 param1 为股票代码 param2 为买入数量
def buy_shares( hwnd, shares_id, number):
    win32gui.SetForegroundWindow(hwnd)# 指定句柄设置为前台，也就是激活
    win32gui.MoveWindow(hwnd,20,20,405,756,True)#改变窗口大小
    hd = find_window( "#32770", "通达信网上交易V6")
    if hd > 0:
        print ("login")
    time.sleep(6)
    # 击交易按钮
    click_mouse( 345, 44)
    time.sleep(6)
    # 点击资金股份
    click_mouse( 92, 576)
    time.sleep(6)
    # 点击买入
    click_mouse( 61,478)
    # 输入股票代码
    input_number_by_key(shares_id)
    # 点击enter
    click_key(13)
    # 再点击enter确认价格
    click_key(13)
    click_key(13)
    # 输入买入股数
    time.sleep(1)
    input_number_by_key(str(number))

    # 输入enter 买入
    click_key(13)
    # 点击确认
    click_mouse( 463,687)
    # 不能夜盘交易取消码
    click_mouse( 505,635)
    # 点击交易，回到原点
    click_mouse( 342,42 )
    #点击行情，回到原点
    click_mouse( 281,40 )
# 点击刷新
def refresh(hwnd):
    win32gui.SetForegroundWindow(hwnd)# 指定句柄设置为前台，也就是激活
    win32gui.MoveWindow(hwnd,20,20,405,756,True)#改变窗口大小
    hd = find_window( "#32770", "通达信网上交易V6")
    if hd > 0:
        print ("login")
    time.sleep(6)
    # 击交易按钮
    click_mouse( 345, 44)
    time.sleep(6)
    # 点击资金股份
    click_mouse( 92, 576)
    click_mouse( 123, 521)
    time.sleep(6)
    click_mouse( 505,635)
    # 点击交易，回到原点
    click_mouse( 342,42 )
    #点击行情，回到原点
    click_mouse( 281,40 )

if __name__=='__main__':
    # hwnd = find_window( "TdxW_MainFrame_Class", "华彩人生牛金岁月V8.01 - [版面-自选股]")
    # if hwnd ==  0:
        #exit()
    # buy_shares( hwnd, '600000',100)
    num = 0
    while 1 == 1 : # 表达式永远为 true
        hwnd = find_window( "TdxW_MainFrame_Class", "华彩人生牛金岁月V8.01 - [版面-自选股]")
        if hwnd ==  0:
            exit()
        num += 1
        print('执行了%s次'%num)
        refresh(hwnd)
        time.sleep(120)
    refresh(hwnd)




'''
66490 小火箭通用加速
132650 C:\APP\python\win32\pywin32_jubin.py - Sublime Text
133208 python3 遍历windows下 所有句柄及窗口名称 - Gamers's blog - CSDN博客 - Google Chrome
3147976 任务管理器
198444 win32
198188 Windows PowerShell
131484 Program Manager
'''