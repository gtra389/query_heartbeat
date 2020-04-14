
# coding: utf-8
import requests
from urllib import urlopen
# from urrlib2 import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from time import gmtime, strftime
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
import os

def creatURL(idN, t):
    string = "http://ec2-54-175-179-28.compute-1.amazonaws.com/get_thinktron_data.php?device_id={}&year_month={}".format(idN,t)
    return string    

def query_data(arg1):
    r = requests.get(arg1) # URL path
    soup = BeautifulSoup(r.text,'lxml')
    a = list(soup.find_all('p'))

    # Split the list through the regular expression
    d = re.split('\s+|,|<br/>|<p>|</p>',str(a))

    # Remove the '' element from the list
    d = list(filter(lambda zz: zz != '', d)) 

    # Remove the '=' element from the list
    d = list(filter(lambda zz: zz != '=', d))

    # Remove the '[' & ']' element from the list
    try:
        d.remove(']')
        d.remove('[')
    except:
        pass
    
    return d

def calculateOFFtime(d):
    
    if ("No" in d) & ("results" in d):
        outputStr = "Offline over 1 month"

    else:    
    # Create a dataframe from the URL by data crawling
        colName=['id', 'time', 'weather', 'air','acceleration','cleavage','incline','field1','field2','field3']
        _Num = 0
        _df  = pd.DataFrame(columns=colName)
        df   = pd.DataFrame(columns=colName)

        for ii in range(0,len(d)):    
            while colName[_Num] in d[ii]:
                _lst = d[ii + 1]
                _lst = _lst.strip(',')

                if _lst == '' or (_lst in colName):
                    _lst = None       

                _df[colName[_Num]] = [_lst] # Put the list into the dataframe
                if _Num < (len(colName)-1):
                    _Num += 1
                else:
                    df = df.append(_df, ignore_index=True)
                    _Num = 0 

        # Convert argument to a numeric type(float64 or int64)
        #numericCol = ['roll', 'pitch', 'yaw','field1','field2','field3']
        #for ii in numericCol:
        #    df[ii] = pd.to_numeric(df[ii])

        # Convert the format of date
        dates = df.time
        df.index = pd.to_datetime(dates.astype(str), format='%Y%m%d%H%M%S')
        df.index.name = 'time'
        del df['time']

        # Check dataframe format
        # df.info()

        # Query the latest time stamp
        lastestTimeStr = df.index[-1]

        # Release the memory
        del df

        # Calculate the offline time
        localTimeStamp = pd.to_datetime(strftime("%Y%m%d%H%M%S"), format="%Y%m%d%H%M%S")
        deltaT = localTimeStamp - lastestTimeStr
        alrTimeIntv = timedelta(minutes = 15)

        if deltaT > alrTimeIntv:

            deltaDay = deltaT.days
            deltaHr  = deltaT.seconds // 3600
            deltaMin = (deltaT.seconds % 3600) // 60
            deltaSec = deltaT.seconds % 60

            outputStr = "Offline time: {} day, {} hr, {} min, {} sec".format(deltaDay,deltaHr, deltaMin, deltaSec)
        else:
            outputStr = "Online"            
    return outputStr

def calculateOFFtime_light(d):
    
    if ("No" in d) & ("results" in d):
        outputStr = "Offline over 1 month"

    else:    
    # Create a dataframe from the URL by data crawling
        colName=['id', 'time', 'weather', 'air','acceleration','cleavage','incline','field1','field2','field3']
        _Num = 0
        _df  = pd.DataFrame(columns=colName)
        df   = pd.DataFrame(columns=colName)

        for ii in range(0,len(d)):    
            while colName[_Num] in d[ii]:
                _lst = d[ii + 1]
                _lst = _lst.strip(',')

                if _lst == '' or (_lst in colName):
                    _lst = None       

                _df[colName[_Num]] = [_lst] # Put the list into the dataframe
                if _Num < (len(colName)-1):
                    _Num += 1
                else:
                    df = df.append(_df, ignore_index=True)
                    _Num = 0 

        # Convert argument to a numeric type(float64 or int64)
        #numericCol = ['roll', 'pitch', 'yaw','field1','field2','field3']
        #for ii in numericCol:
        #    df[ii] = pd.to_numeric(df[ii])

        # Convert the format of date
        dates = df.time
        df.index = pd.to_datetime(dates.astype(str), format='%Y%m%d%H%M%S')
        df.index.name = 'time'
        del df['time']

        # Check dataframe format
        # df.info()

        # Query the latest time stamp
        lastestTimeStr = df.index[-1]

        # Release the memory
        del df

        # Calculate the offline time
        localTimeStamp = pd.to_datetime(strftime("%Y%m%d%H%M%S"), format="%Y%m%d%H%M%S")
        deltaT = localTimeStamp - lastestTimeStr
        alrTimeIntv = timedelta(minutes = 15)

        if deltaT > alrTimeIntv:

            deltaDay = deltaT.days
            deltaHr  = deltaT.seconds // 3600
            deltaMin = (deltaT.seconds % 3600) // 60
            deltaSec = deltaT.seconds % 60

            outputStr = "Offline time: {} day, {} hr".format(deltaDay,deltaHr)
        else:
            outputStr = "Online"            
    return outputStr

locationList = ["NewTaipei", "Taipei"]
#locationList = ["Taipei"]
saveFid  =[]

for location in locationList:
    idNumList = []
    DBName =""
    queryDate = strftime("%Y%m%d")
    quertMonth = strftime("%Y%m")
    now = strftime("%Y%m%d%H%M")

    if (location.lower() == "newtaipei"):
        idNumDict  = [{'name':'馥記山莊','id':'2015'}, # 0
                      {'name':'秀岡第一','id':'3015'}, # 1
                      {'name':'老爺山莊','id':'2011'}, # 2
                      {'name':'老爺山莊','id':'1007'}, # 3
                      {'name':'怡園社區','id':'3014'}, # 4
                      {'name':'台北小城','id':'3001'}, # 5
                      {'name':'秀岡陽光','id':'3029'}, # 6
                      {'name':'薇多綠雅','id':'3028'}, # 7
                      {'name':'達觀鎮B6','id':'3022'}, # 8
                      {'name':'花園點二','id':'2005'}, # 9 
                      {'name':'花園點二','id':'1005'},
                      {'name':'達觀鎮A1','id':'3019'},
                      {'name':'圓富華城','id':'3021'},              
                      {'name':'淺水灣莊','id':'3023'},
                      {'name':'詩畫大樓','id':'3016'},
                      {'name':'伯爵晶鑽','id':'3025'},
                      {'name':'花園點一','id':'2009'},
                      {'name':'勘農別墅','id':'2010'},
                      {'name':'勘農別墅','id':'1008'},
                      {'name':'國家別墅','id':'3017'},
                      {'name':'台北山城','id':'3024'},
                      {'name':'歡喜居易','id':'3013'},
                      {'name':'伯爵一期','id':'3020'},
                      {'name':'迎旭山莊','id':'3018'},
                      {'name':'水蓮山莊','id':'2022'},
                      {'name':'新雪梨  ','id':'3030'},
                      {'name':'伯爵幼兒','id':'3032'},
                      {'name':'仁愛特區','id':'3035'},
                      {'name':'詩畫管理','id':'3036'}]
        DBName = "New Taipei"
    elif (location.lower() == "taipei"):
        idNumDict  = [{'name':'政大自強','id':'2007'},
                      {'name':'政大山頂','id':'2001'},
                      {'name':'政大山頂','id':'1001'},
                      {'name':'中山北七','id':'2008'},
                      {'name':'中山北七','id':'1003'},
                      {'name':'公訓新牆','id':'2003'},
                      {'name':'公訓舊牆','id':'2002'},
                      {'name':'公訓舊牆','id':'1002'},
                      {'name':'松德院北','id':'2021'},
                      {'name':'松德院北','id':'6001'},
                      {'name':'松德院北','id':'8001'},
                      {'name':'松德院南','id':'2020'},              
                      {'name':'松德院南','id':'6002'},
                      {'name':'永春高中','id':'2023'},
                      {'name':'永春高中','id':'6003'},
                      {'name':'世界山莊','id':'3031'},
                      {'name':'世說新語','id':'3037'},
                      {'name':'夏木漱石','id':'3034'},
                      {'name':'玫瑰城社','id':'3033'}]
        DBName = "Taipei"
    else:
        print("No such name.")


    flag = 0
    for ii in range(0, len(idNumDict)):       
        URLstr = creatURL(str(idNumDict[ii]["id"]),queryDate) # Format in (id_Num, yyyymm)
        # print("Look at here:" + URLstr)
        qD = query_data(URLstr)

        if ("No" in qD) & ("results" in qD):
            print("{} Offline over 1 day".format(idNumDict[ii]["id"]))
            URLstr = creatURL(str(idNumDict[ii]["id"]),quertMonth)
            qD = query_data(URLstr)    

        writingStr = calculateOFFtime(qD)

        if (ii == 0):
            queryFid = "{}_hearbeatList.txt".format(DBName)
            saveFid  += [queryFid]

        if (flag == 0):
            with open(queryFid, "a") as file:
                file.write("---------------Device heartbeat---------------")
                file.write("\n")
                file.write("Name of project: " + DBName)
                file.write("\n")
                file.write("Query time: {}".format(strftime("%Y/%m/%d %H:%M")))
                file.write("\n")
                flag = 1   
        with open(queryFid, "a") as file:
            writing = "{}    {}    {}".format(idNumDict[ii]["name"],idNumDict[ii]["id"],writingStr)
            file.write(writing)
            file.write("\n")
        print(str(idNumDict[ii]["id"]) + "  Done.")

# Send a e-mail
smtpssl=smtplib.SMTP_SSL("smtp.gmail.com", 465)
smtpssl.ehlo()
smtpssl.login("n86024042@gmail.com", "ibovbvqwpobuofqb")

msg = ""
for ii in range(0, len(saveFid)):    
    with open(saveFid[ii],'r') as file:
        msg += file.read()       
        
mime = MIMEText(msg, "plain", "utf-8")
mime["Subject"] = "Icebergtek Device heartbeat\n"
msgEmail        = mime.as_string()  

to_addr  = ["ian@icebergtek.com",
            "odie@icebergtek.com",
            "white@icebergtek.com",
            "jim@icebergtek.com",
            "meichi@thinktronltd.com",
            "james.wang@icebergtek.com"]

#to_addr  = ["ian@icebergtek.com"]          

status = smtpssl.sendmail("n86024042@gmail.com", 
                          to_addr, 
                          msgEmail)
if status == {}:
    print("Sending e-mail is done.")
    smtpssl.quit()
    
    try:
        os.remove("/home/pi/query_heartbeat/"+saveFid[0])
        os.remove("/home/pi/query_heartbeat/"+saveFid[1])

    except OSError as e:
        print(e)
    else:
        print("The file is deleted successfully")

else:
    print("Failed to transmit.")
    smtpssl.quit()
