#!/usr/bin/env python

## Lost and Found - Client Monitor Version
## This Application will help you retreive a lost item by looking up it's last known location.
## This version only uses the client Monitor API, and returns the last AP the device was connected to within the last 2 weeks.


import requests #to fire off HTTP requests
import datetime #to get the current date, and format dates for the APIs
#import csv      #to read & write CSV files
#import sys      #to create the progress indicator and print directly to the console.
import time     #to sleep & add timers.
#import os       # to clear the screen.

#---Variables you will need to setup for your application:
#See http://developer.aerohive.com and navigate to 'My Applications'
clientID = "YOUR-CLIENT-ID"
clientSecret = "YOUR-CLIENT-SECRET"
redirectURL = "https://mysite.com"
UTCoffset = '-08:00' # Your timezone - not critical for lost & found since we're not seperating days but still needed for API calls.
# Let's not perster users for theirs, but of you want to change it here it is...


#------Variables for NG interaction
baseUrl = 'https://cloud-va.aerohive.com/xapi'
# VHM ID: to be changed to target VHM
ownerID = ""
# These are the headers we will use to interact with the APIs. Authorization will need to be updated with the access token.
headers= {'Authorization':'Bearer ', 'X-AH-API-CLIENT-ID':clientID, 'X-AH-API-CLIENT-SECRET':clientSecret, 'X-AH-API-CLIENT-REDIRECT-URI':redirectURL}



#------Begin Application
print "\n\nAerohive Location Engine Demo - Location Reporting"
print "Written by: Daniel O'Rorke (dororke@aerohive.com)"
print "(c) 2016 Aerohive Networks"
print "This application will help you find a lost device by using Aerohive Location APIs."
print "This version only uses the client Monitor API, and returns the last AP the device was connected to within the last 2 weeks."


#-----Prompt user for input
print "\n\n\n\n\n\nI need to know a few things so we can log you in."
print "What data center are you using?"
print "1. North America"
print "2. Europe"
userEntry = int(raw_input("Enter the NUMBER of your data center: "))
if userEntry == 1:
    baseUrl = "https://cloud-va.aerohive.com/xapi"
else:
    baseUrl = "https://cloud-ie.aerohive.com/xapi"

print "Great!\nNow I need the VHM number. You can find it by clicking 'about' in the NG console."
userEntry = raw_input("Enter your VHM number: ")
ownerID = userEntry
print "Fantastic.\nNow one last thing: your keys to the kingdom.\nYour Access Token can be generated in NG under Settings>Token Managment. Use Client ID: "+clientID
userEntry = raw_input("Enter your access token: ")
accessToken = userEntry


headers["Authorization"] = "Bearer "+accessToken

#---Query the Monitoring API for a list of clients.
# Build Client Monitoring API URL
# https://cloud-va.aerohive.com/xapi/v1/location/clients/?ownerId=1265
clientMonURL = "/v1/monitor/clients/"
queryParams = "?ownerId="+ownerID
url = baseUrl+clientMonURL+queryParams
print "Requesting: "+url
# Request data for all clients
response = requests.get(url, headers=headers)
print "Monitoring API response code: "+str(response.status_code)
JSON = response.json()

userNames= []
for client in JSON["data"]: #Make a list of usernames
    if client["userName"] not in userNames:
        userNames.append(client["userName"])
userNames.sort()

i=1
print "What is your user name?"
for userName in userNames:
    print str(i)+". "+userName
    i += 1

userEntry = int(raw_input("Enter the NUMBER of your user name: "))
usersName = userNames[userEntry-1]


#---Query the Monitoring API for a list of clients for the last 2 weeks.
# https://cloud-va.aerohive.com/xapi/v1/monitor/clients?ownerId=1265&startTime=2016-01-08T00:00:00.000Z&endTime=2016-01-08T01:00:00.000Z&timeunit=OneDay
timeEnd = datetime.datetime.now() # End time should be today
timeBegin = timeEnd - datetime.timedelta(days=14) #2 weeks ago
queryParams = '?ownerId='+str(ownerID)+'&startTime='+timeBegin.isoformat()+UTCoffset+'&endTime='+timeEnd.isoformat()+UTCoffset+'&timeunit=OneDay'
url = baseUrl+clientMonURL+queryParams
response = requests.get(url, headers=headers)
print "Client Monitoring API response code: "+str(response.status_code)
JSON = response.json()
myClients = []
i=1
for client in JSON["data"]:
    if client["userName"] == usersName:
        myClients.append(client["clientMac"])
        print str(i)+". "+client["clientMac"]+" | "+client["hostName"]
        i += 1 # increment i by 1
        
userEntry = int(raw_input("Enter the NUMBER of the lost device: "))
lostDeviceMac = myClients[userEntry-1]

##---Since we have the client monitoring data already, let's just use that to get the last AP the device was connected to.
lastAPConnectedID = ""
for client in JSON["data"]:
    if client["clientMac"] == lostDeviceMac:
        lastAPConnectedID = client["deviceId"] # This will keep getting set every time we see the MAC, so the last value should be the most recent.

##---We need the AP name, so let's look it up.
# Query the Device Monitoring API:
# https://cloud-va.aerohive.com/xapi/v1/monitor/devices/{deviceID}?ownerId=1265
deviceMonURL = "/v1/monitor/devices/"+str(lastAPConnectedID)
queryParams = "?ownerId=1265"
url = baseUrl+deviceMonURL+queryParams
response = requests.get(url, headers=headers)
print "Device Monitoring API response code: "+str(response.status_code)
JSON = response.json()
APName = JSON["data"]["hostName"]
    

print "\n\nLast connected to: " + APName
    


##---Query the Location API for the last known location of the device.
## Currently, the Location API only gets data for NOW. In the future, this will need to be updated to fetch data from the past.
## https://cloud-va.aerohive.com/xapi/v1/location/clients/?ownerId=1265
#timeEnd = datetime.datetime.now() # End time should be today
#timeBegin = timeEnd - datetime.timedelta(days=14) #2 weeks ago
#locationURL = "/v1/location/clients/"
#queryParams = '?ownerId='+str(ownerID)
#url = baseUrl+locationURL+queryParams
#response = requests.get(url, headers=headers)
#print "Location API response code: "+str(response.status_code)
#JSON = response.json()
#for AP in JSON["data"]:
#    for client in AP["observations"]:
#        if client["clientMac"] == lostDeviceMac:
#            print "Last known location: X: " + str(client["x"]) + "Y: " + str(client["y"]) + "\t Seen: " + str(client["seenTime"])
