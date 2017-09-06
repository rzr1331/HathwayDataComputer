import urllib2
import urllib
import os
import re
from datetime import date, datetime
import time
from bs4 import BeautifulSoup
import requests
import sys
import json
from flask import Flask, render_template

app = Flask('UsageCal')
@app.route('/')

def index():
    global uploaded,downloaded,total
    return render_template('index.html',startDate=getStartDate(),endDate=getEndDate(),uploaded=uploaded,downloaded=downloaded,total=total,remaining=remaining)

def getStartDate():
    currentDate = datetime.now()
    currentMonth = currentDate.month
    currentDay = currentDate.day
    currentYear = currentDate.year
    if currentDay <= 22:
        startDay = 22
        if currentMonth > 1:
            startMonth = currentMonth - 1
            startYear = currentYear
        elif currentMonth == 1:
            startMonth = 12
            startYear = currentYear - 1
    else:
        startDay = 22
        startMonth = currentMonth
        startYear = currentYear
    return str(startDay) + "/" + str(startMonth) + "/" + str(startYear);

def getEndDate():
    currentDate = datetime.now()
    currentMonth = currentDate.month
    currentDay = currentDate.day
    currentYear = currentDate.year
    return str(currentDay) + "/" + str(currentMonth) + "/" + str(currentYear)

def getStartTimestamp():
    dateStr = getStartDate()
    print "Start Date: " + dateStr
    timestamp = time.mktime(time.strptime(dateStr, "%d/%m/%Y"))
    return int(timestamp)

def getEndTimestamp():
    currentDate = datetime.now()
    currentMonth = currentDate.month
    currentDay = currentDate.day
    currentYear = currentDate.year
    dateStr = str(currentDay) + "/" + str(currentMonth) + "/" + str(currentYear)
    print "End Date: " + dateStr
    timestamp = time.mktime(time.strptime(dateStr, "%d/%m/%Y"))
    return int(timestamp)

def getUsageNumber(strVal):
    val = strVal.replace(" MB", "")
    val = val.replace(",", "")
    valInt = float(val)
    return valInt


URL= 'http://isp.hathway.net:7406/selfcare/index.php?r=login/loginas'
soup = BeautifulSoup(urllib2.urlopen(URL),'html.parser')

uploaded = 0
downloaded = 0
total = 0
remaining = 350
password='pass'
username='user'

def main():
    global uploaded,downloaded,total,remaining,password,username
    # Start a session so we can have persistant cookies
    # Session() >> http://docs.python-requests.org/en/latest/api/#request-sessions
    session = requests.Session()

    # This is the form data that the page sends when logging in
    # You are wrongly using string values instead of the intended variables here that is RegisterNumber and not 'RegisterNumber'
    login_data = {
    'AJAX_REQUEST_ENABLE'   : 'true',
    'password' : password,
    'servicetype' : 'BB',
    'username' : username
    }
    print login_data

    # Authenticate
    r = session.post(URL, data = login_data)
    # print "POST DETAILS : "
    # print r.content
    # Try accessing a page that requires you to be logged in

    startDate = getStartTimestamp()
    endDate = getEndTimestamp()

    usage_data = {
    'AJAX_REQUEST_ENABLE' : 'true',
    '_search' : 'false',
    'end_date' : str(endDate),
    'nd' : '1504692301081',
    'page' : '1',
    'rows' : '10',
    'sidx' : 'effective_t',
    'sord' : 'desc',
    'start_date' : str(startDate)
    }

    r = session.post('http://isp.hathway.net:7406/selfcare/index.php?r=site/usage_details', data = usage_data)
    print "Usage Response : "
    print r.content
    data = json.loads(r.content)
    for item in data:
        uploaded = uploaded + getUsageNumber(item["bytes_uplink"])
        downloaded = downloaded + getUsageNumber(item["bytes_downlink"])
        total = total + getUsageNumber(item["total_data"])
    uploaded = int(uploaded / 1024)
    downloaded = int(downloaded / 1024)
    total = int(total / 1024)
    remaining = remaining - total
    print uploaded
    print downloaded
    print total
    print remaining

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0',debug=True)
