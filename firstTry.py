from tkinter import *
from tkinter.filedialog import askopenfilename
import time
import requests
import math
import json
import cuki2sepidz.CounterApps as CA

root = Tk()
root.title("Cuki2CounterApps")
root.iconbitmap("./logo64x64.ico")
root.geometry("500x300")
root.resizable(0, 0)

username = ''
password = ''
token = ''
NotSubmittedOrders = []
appCounterObject = None


def connected_to_internet(url='http://www.google.com/', timeout=3):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False


def login():
    if not connected_to_internet():
        statusLabel.config(text="عدم اتصال به اینترنت")
        return False

    statusLabel.config(text="...منتظر ورود")
    global username, password, token
    username = usernameInput.get()
    password = passwordInput.get()

    url = "https://api.cuki.ir/v201/res/loginRes.fetch.php"
    loginParams = {
        "username": username,
        "password": password
    }
    try:
        r = requests.post(url=url, data=loginParams)
        rData = r.json()
        if rData['statusCode'] == 401:
            statusLabel.config(text="یوزرنیم یا پسورد اشتباه است. دوباره امتحان کنید")
        elif rData['statusCode'] == 200:
            statusLabel.config(text="رستوران:" + rData["data"]["resPersianName"])
            token = rData["data"]['token']
            loginFrame.destroy()
            getOrderList(token)
            selectCounterAppFrame.pack()
            return rData["data"]
        else:
            statusLabel.config(text="اتفاقی رخ داد. دوباره امتحان کنید")
    except:
        statusLabel.config(text="اتفاقی رخ داد. دوباره امتحان کنید")


def getOrderList(_token):
    url = "https://api.cuki.ir/v201/res/getOrdersList.fetch.php"

    currentTime = math.floor(time.time())
    getOrderListParams = {
        "token": _token,
        "startDate": currentTime - (86400 * 5),
        "endDate": currentTime
    }
    try:
        r = requests.post(url=url, data=getOrderListParams)
        rData = r.json()
        if rData['statusCode'] == 200:
            getNotSubmittedOrders(rData["data"])
            return rData["data"]
        else:
            print("اتفاقی رخ داد. دوباره امتحان کنید")
    except:
        statusLabel.config(text="اتفاقی رخ داد. دوباره امتحان کنید")


def getNotSubmittedOrders(ordersList):
    global NotSubmittedOrders
    resultArr = []
    for eOrder in ordersList:
        if int(eOrder["counter_app_status"]) == 0:
            orderFoods = {"table": 0, "trackingId": 0, "phone": 0, "foodList": []}
            for eFood in json.loads(eOrder["order_list"]):
                orderFoods["foodList"].append({"foodId": eFood["counterAppFoodId"], "number": eFood['number']})

            orderFoods["table"] = eOrder["order_table"] if int(eOrder["order_table"]) > 0 else eOrder["address"]
            orderFoods["phone"] = eOrder["customer_phone"]
            orderFoods["trackingId"] = eOrder["tracking_id"]
            resultArr.append(orderFoods)
    NotSubmittedOrders = resultArr
    return resultArr


def submitOrderSavedOnCuki(trackingId):
    url = "https://api.cuki.ir/v201/res/submitOrderSavedCounterApp.modify.php"

    global token
    submitSavedParams = {
        "token": token,
        "trackingId": trackingId,
    }

    try:
        r = requests.post(url=url, data=submitSavedParams)
        rData = r.json()
        if rData['statusCode'] == 200:
            getNotSubmittedOrders(rData["data"])
            return rData["data"]
        else:
            print("اتفاقی رخ داد. دوباره امتحان کنید")
    except:
        statusLabel.config(text="اتفاقی رخ داد. دوباره امتحان کنید")


def selectSepidz():
    global appCounterObject
    with open("./filePath.txt", "r") as fileReader:
        try:
            fileContentDic = json.loads(fileReader.read())
            if len(fileContentDic['sepidz']) > 5 and fileContentDic['sepidz'][-7:] == "ant.exe":
                appCounterObject = CA.Cuki2Cpeds_SaveOrders(statusLabel)
                if appCounterObject.start(fileContentDic['sepidz']):
                    statusLabel.config(text="")
                    selectCounterAppFrame.destroy()
                    insertInfoAppFrame.pack()
                else:
                    pass
            else:
                statusLabel.config(text="فایل سپیدز یافت نشد. لطفا آن را انتخاب کنید")
                getFilePath()
        except:
            statusLabel.config(text="فایل سپیدز یافت نشد. لطفا آن را انتخاب کنید")
            getFilePath()


def importOrderInSepidz(table, foodList, action):
    appCounterObject.setTable(table)
    appCounterObject.enterFoods(foodList)
    if action == "save":
        if appCounterObject.saveNoPrint():
            return True
        else:
            return False
    else:
        return False


def submitImportOrdersInSepidz():
    global NotSubmittedOrders, token

    if len(NotSubmittedOrders) == 0:
        statusLabel.config(text="سفارش جدیدی برای وارد کردن یافت نشد.")
        getOrderList(token)

    if appCounterObject.salonIsTopWindow():
        copyNSO = NotSubmittedOrders.copy()
        for eOrder in copyNSO:
            if importOrderInSepidz(eOrder['table'], eOrder['foodList'], "save"):
                submitOrderSavedOnCuki(eOrder['trackingId'])
                NotSubmittedOrders.remove(eOrder)
                statusLabel.config(text=" سفارش " + eOrder['trackingId'] + " ذخیره شد ")


def getNewOrders():
    getOrderList(token)
    if len(NotSubmittedOrders) == 0:
        statusLabel.config(text="سفارش جدیدی یافت نشد.")
    else:
        statusLabel.config(text=" تعداد " + str(len(NotSubmittedOrders)) + " سفارش یافت شد ")
def getFilePath():
    with open("./filePath.txt", "r") as fileReader:
        fileContentDic = {"sepidz": "", "hami": ""}
        try:
            fileContentDic = json.loads(fileReader.read())
            print(fileContentDic['sepidz'])
            print(fileContentDic['hami'])
        except:
            pass
        path = askopenfilename()
        if len(path) > 5:
            fileContentDic['sepidz'] = path
        with open("./filePath.txt", "w") as fileWriter:
            fileWriter.write(json.dumps(fileContentDic))
    return fileContentDic['sepidz']


# login frame
loginFrame = LabelFrame(root, text="ورود", labelanchor='ne', pady=10, padx=10)
usernameLabel = Label(loginFrame, text=":نام کاربری")
usernameLabel.grid(row=0, column=2, pady=3)
usernameInput = Entry(loginFrame)
usernameInput.grid(row=0, column=1, pady=3)
passwordLabel = Label(loginFrame, text=":رمز عبور")
passwordLabel.grid(row=1, column=2, pady=3)
passwordInput = Entry(loginFrame, show="*")
passwordInput.grid(row=1, column=1, pady=3)
loginButton = Button(loginFrame, text="ورود", padx=20, command=login)
loginButton.grid(row=2, column=1, pady=10)
emptyLabelToJustify1 = Label(loginFrame, padx=20).grid(row=0, column=0)
loginFrame.pack()

# select counter app
selectCounterAppFrame = LabelFrame(root, text="نرم افزار حسابداری جهت اتصال", labelanchor='ne', pady=10, padx=10)
sepidzButton = Button(selectCounterAppFrame, text="سپیدز", padx=15, command=selectSepidz).grid(row=0, column=2)
hamiButton = Button(selectCounterAppFrame, text="حامی", padx=15, state=DISABLED).grid(row=0, column=0)
emptyLabelToJustify2 = Label(selectCounterAppFrame, padx=30).grid(row=0, column=1)

# select insert info
insertInfoAppFrame = LabelFrame(root, text="ثبت سفارشات 24 ساعت گذشته", labelanchor='ne', pady=20, padx=40)
insertInfoButton = Button(insertInfoAppFrame, text="ثبت اطلاعات", padx=15, command=submitImportOrdersInSepidz).pack()
getNewOrdersButton = Button(insertInfoAppFrame, text="دریافت اطلاعات جدید", padx=15, command=getNewOrders).pack(pady=10)


# status bar frame
statusFrame = Frame(root, bd=2, relief=SUNKEN)
statusLabel = Label(statusFrame, text="...منتظر ورود")
statusLabel.pack(side=RIGHT)
statusFrame.pack(side=BOTTOM, fill=X)

root.mainloop()
