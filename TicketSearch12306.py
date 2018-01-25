#!/usr/bin/env.python
# _*_ coding:utf-8 _*_

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import random
from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient

# 发送短信
def sendMessage(telephoneNum, TEXT):
    client = YunpianClient('此处填入云片的apikey，需要自己去注册申请')
    param = {YC.MOBILE: telephoneNum, YC.TEXT: TEXT}
    r = client.sms().single_send(param)
    print(r.msg(), r.data(), r.detail(), sep='\n')


# 输入乘车信息
def userInput1():
    global inputFrom, inputDestination, inputDate, telephoneNum
    print("-------------------输入乘车信息------------------")
    inputFrom = input("请输入出发地：")
    inputDestination = input("请输入到达地：")
    inputDate = input("请输入出发时间（格式:xxxx-xx-xx）：")
    telephoneNum = input("请输入接收提示消息的手机号：")
    print("------------------------------------------------")


# 输入购票需求,在这之前必须先进行一次查询来告诉用户可抢票选车次和座位
def userInput2(trainNum, trainTime):
    global seatType, inputTrainNum, inputSeatType
    seatType = ['商务座', '一等座', '二等座', '高级软卧',
                '软卧', '动卧', '硬卧', '软座', '硬座', '无座', '其他']
    print("-------------------可选车次-------------------")
    print("编号 | 车次号 |  发车    到站    历时")
    for i in range(len(trainNum)):
        print("%3s | %5s |  %s" % (i + 1, trainNum[i], trainTime[i]))
    print("------------------可选座位类型------------------")
    print("编号 | 座位类型")
    for i in range(11):
        print("%3s |  %s" % (i + 1, seatType[i]))
    print("---------------输入查询车次和座位----------------")
    # 用户输入要选择的车次和座位类型
    inputTrainNum = input("请输入要选择的车次对应编号，以空格分开：")
    inputSeatType = input("请输入作席类型，以空格分开：")
    # 对用户输入信息提取
    inputTrainNum = re.findall("[0-9]+", str(inputTrainNum))
    inputSeatType = re.findall("[0-9]+", str(inputSeatType))
    print("------------------------------------------------")


# 判断本次查询是否有符合要求的座位，并返回结果
def check(TicketInfo):
    a = []
    for i in inputSeatType:
        seat = int(i) + 1
        for j in inputTrainNum:
            train = int(j) - 1
            if TicketInfo[seat][train] >= 1:
                a.append([seat, train])
    return a


# 将网页信息转化为可处理信息
def resultSolve(result):
    global trainNum, trainTime
    # 车次
    trainNum = re.findall("[A-Z][0-9]+", result)
    # 发车时间，到站时间，历时
    trainTime = re.findall("[0-9]{2}:[0-9]{2}.[0-9]{2}:[0-9]{2}.[0-9]{2}:[0-9]{2}", result, re.S)
    for i in range(len(trainTime)):
        trainTime[i] = re.sub(r"\n", repl=r"   ", string=trainTime[i])
    # 余票数量
    TicketNum = re.findall("((?<=\n)[0-9]+(?=\n))", result)
    n = int(len(TicketNum) / len(trainNum))  # 作席类别数目
    SWZ = []
    for i in range(len(trainNum)):
        SWZ.append(int(TicketNum[n * i + 0]))
    YDZ = []
    for i in range(len(trainNum)):
        YDZ.append(int(TicketNum[n * i + 1]))
    EDZ = []
    for i in range(len(trainNum)):
        EDZ.append(int(TicketNum[n * i + 2]))
    GJRW = []
    for i in range(len(trainNum)):
        GJRW.append(int(TicketNum[n * i + 3]))
    RW = []
    for i in range(len(trainNum)):
        RW.append(int(TicketNum[n * i + 4]))
    DW = []
    for i in range(len(trainNum)):
        DW.append(int(TicketNum[n * i + 5]))
    YW = []
    for i in range(len(trainNum)):
        YW.append(int(TicketNum[n * i + 6]))
    RZ = []
    for i in range(len(trainNum)):
        RZ.append(int(TicketNum[n * i + 7]))
    YZ = []
    for i in range(len(trainNum)):
        YZ.append(int(TicketNum[n * i + 8]))
    WZ = []
    for i in range(len(trainNum)):
        WZ.append(int(TicketNum[n * i + 9]))
    QT = []
    for i in range(len(trainNum)):
        QT.append(int(TicketNum[n * i + 10]))
    TicketInfo = [trainNum, trainTime, SWZ, YDZ, EDZ, GJRW, RW, DW, YW, RZ, YZ, WZ, QT]
    return TicketInfo


# 主函数，从这开始执行
def main():
    # 输入乘车信息
    userInput1()
    print("正在处理...")
    # 选择查询所使用浏览器，需要安装相应浏览器的开发者工具
    browser = webdriver.Chrome()
    try:
        # 打开订票查询网页
        browser.get("https://kyfw.12306.cn/otn/leftTicket/init")
        time.sleep(0.5)
        # 输入出发地
        From = browser.find_element_by_id("fromStationText")
        From.click()
        From.send_keys(inputFrom)
        From.send_keys(Keys.RETURN)
        time.sleep(0.5)
        # 输入目的地
        To = browser.find_element_by_id("toStationText")
        To.click()
        To.send_keys(inputDestination)
        To.send_keys(Keys.RETURN)
        time.sleep(0.5)
        # 去掉日期栏只读属性
        js = "document.getElementById('train_date').removeAttribute('readonly')"
        browser.execute_script(js)
        # 输入日期
        date = browser.find_element_by_id("train_date")
        date.clear()
        date.send_keys(inputDate)
        time.sleep(0.5)
        # 第一次查询，返回车次作席信息给用户以方便用户选择，第一次缓存，查询时间长一些
        browser.find_element_by_id("query_ticket").click()
        time.sleep(10)
        result = browser.find_element_by_id("queryLeftTable").text
        result = re.sub(r"\s", repl=r"\n", string=result)
        result = re.sub(r"-----|------", repl='00:00', string=result)
        result = re.sub(r"--|\*|无", repl='0', string=result)
        result = re.sub(r"有", repl='100', string=result)
        TicketInfo = resultSolve(result)
        # 用户输入想要抢票的类型
        userInput2(trainNum, trainTime)
        # 输入查询间隔时间，开始查询
        print("正在查询，若有票将会第一时间短信通知您，请耐心等待...")
        while True:
            count = 0
            try:
                # 设置查询时间间隔
                span = random.uniform(2, 5)
                time.sleep(span)
                # 点击查询按钮，返回结果
                browser.find_element_by_id("query_ticket").click()
                time.sleep(3)
                result = browser.find_element_by_id("queryLeftTable").text
                # 对结果进行提取
                result = re.sub(r"\s", repl=r"\n", string=result)
                result = re.sub(r"--|\*|无", repl='0', string=result)
                result = re.sub(r"有", repl='100', string=result)
                # 调用信息处理模块，得到车次和余票信息
                TicketInfo = resultSolve(result)
                # 根据用户需求筛选出是否有符合需求信息
                getTicket = check(TicketInfo)
                if getTicket:
                    print("-------------------查询到---------------------")
                    typeNum = len(getTicket)
                    Train, Seat, Num = [], [], []
                    Ticket = ""
                    for i in range(typeNum):
                        Train.append(TicketInfo[0][getTicket[i][1]])
                        Seat.append(seatType[getTicket[i][0] - 2])
                        if TicketInfo[getTicket[i][0]][getTicket[i][1]] == 100:
                            TicketInfo[getTicket[i][0]][getTicket[i][1]] = '很多'
                        Num.append(TicketInfo[getTicket[i][0]][getTicket[i][1]])
                        Ticket = Ticket + Train[i] + "有" + Seat[i] + str(Num[i]) + "张"
                    print(Ticket)
                    message = "【LYK火车票】" + "帮您查询到下列车次有票" + Ticket + "。"
                    sendMessage(telephoneNum, message)
                    print("----------------------------------------------")
                    break
            except Exception as e:
                count += 1
                if count >= 10:
                    browser.quit()
                    print(e, "请检查网络环境是否正常！", sep='\n')
                    main()
                else:
                    continue
    except Exception as e:
        browser.quit()
        print(e, "请检查网络环境是否正常！", sep='\n')
        main()


main()
