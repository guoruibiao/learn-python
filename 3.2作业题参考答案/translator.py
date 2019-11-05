#!/usr/bin/env python3
# coding: utf8
"""
打算使用这个翻译接口
http://fy.iciba.com/ajax.php?a=fy&from=auto&to=auto&w=hello%20world
"""
import os
import json
import tkinter
import requests
import subprocess
from urllib import parse

def getClipboardText():
    """
    如果是纯文本，则可以返回二进制的内容；
    剪切板内非纯文本数据时，返回空字符串。
    :return:
    """
    pipe = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = pipe.wait()
    bytes = pipe.stdout.read()
    return bytes.decode("utf8")

def getTranslateResult(raw):
    """
    即使代码出错，也要合理控制输出，给提示一个文案
    :param raw: 系统剪切板的内容直接
    :return:
    """
    result = "出错啦，没翻译出来"
    words = parse.quote(raw)
    url = "http://fy.iciba.com/ajax.php?a=fy&from=auto&to=auto&w=" + words
    response = requests.get(url=url)
    if response.status_code == 200:
        try:
            jsondata = json.loads(response.text)
            # print(response.text)
            if "content" in jsondata.keys():
                if "out" in jsondata["content"].keys():
                    result = jsondata["content"]["out"]
                elif "word_mean" in jsondata["content"].keys():
                    result = jsondata["content"]["word_mean"]
        except Exception as e:
            print(e)
    return result

# 制作GUI 有时候复制了内容却不想去进行翻译，就可以使用开关关掉翻译
class App:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry('300x50')
        self.root.title("翻译小助手")
        self.button = tkinter.Button(text="开关", command=self.update_label)
        self.labelText = tkinter.StringVar()
        self.buttonStatus = tkinter.BooleanVar()
        self.labelText.set("您可以通过点击按钮来打开/关闭翻译服务")
        self.label = tkinter.Label(textvariable=self.labelText)
        self.button.pack()
        self.label.pack()
        # 首次开启服务
        self.update_clock()
        # 记录一下首次翻译历史
        self.lastTranslateText = ""
        self.buttonStatus = 1

    def update_label(self):
        self.buttonStatus = 1 if self.buttonStatus == 0 else 0
        self.labelText.set("翻译服务已开启") if self.buttonStatus == 1 else self.labelText.set("翻译服务已关闭")
        print("开关状态：", self.buttonStatus)

    def doTranslate(self):
        if self.buttonStatus == 1:
            rawtext = getClipboardText()
            if self.lastTranslateText != rawtext:
                translateResult = getTranslateResult(rawtext)
                self.lastTranslateText = rawtext
                # print("翻译结果：", translateResult)
                os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(translateResult, rawtext))

    def start(self):
        self.root.mainloop()

    def update_clock(self):
        self.root.after(1000, self.update_clock)
        self.doTranslate()

# 程序入口
if __name__ == "__main__":
    app = App()
    app.start()
