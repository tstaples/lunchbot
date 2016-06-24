# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import json
import requests
from slackclient import SlackClient
from foodtruck import FoodTruck


def readFirstLineOfFile(path):
    text = None
    try:
        f = open(path, "r")
        text = f.read()
        f.close()
    except Exception as ex:
        print("Error reading file: " + str(ex))
    return text


def getFoodTrucks():
    # TODO: cache response and expire once per day
    region = readFirstLineOfFile("config/region.txt")
    if not region:
        print("Failed to get region from config file")
        return []

    rjson = None
    try:
        #response = requests.get("http://data.streetfoodapp.com/1.1/schedule/region")
        #rjson = response.json()
        rjson = json.load(open("response.json", "r")) # temp for testing so we don't spam requests
    except Exception as ex:
        print("Error: " + str(ex))
        return []

    # Get the full display name of the region
    regionDisplayName = region
    if "regions" not in rjson or len(rjson["regions"]) == 0:
        print("Response had no region information")
    else:
        regionDisplayName = rjson["regions"][0]["name"]

    foodTrucks = []
    vendorsObj = rjson["vendors"]
    for vendorName in vendorsObj:
        foodTruck = FoodTruck(vendorName, vendorsObj[vendorName], regionDisplayName)
        foodTrucks.append(foodTruck)
    return foodTrucks


def getTodaysFoodTruck():
    foodtrucks = getFoodTrucks()
    for foodtruck in foodtrucks:
        if foodtruck.isOpen():
            return foodtruck
    #return None
    return foodtrucks[0] # temp for testing


def boldText(txt):
    return "*" + txt + "*"


def getCurrentFoodTruckInfo():
    foodtruck = getTodaysFoodTruck()
    if not foodtruck:
        return None
    msg = boldText(foodtruck.name) + "\n"
    msg += foodtruck.description + "\n"
    msg += foodtruck.getFormattedHoursOfOperation() + " at " + foodtruck.location + "\n"
    msg += "Pay with: " + foodtruck.getFormattedPaymentMethods() + "\n"
    msg += foodtruck.getStreetFoodAppUrl()
    return msg


def getValueOrDefault(arr, key, defaultValue = None):
    if arr and key in arr:
        return arr[key]
    return defaultValue

##################################################################

api_key = readFirstLineOfFile("config/api_token.txt")
client = SlackClient(api_key)

if client.rtm_connect():
    while True:
        time.sleep(1)
        last_read = client.rtm_read()
        if last_read:
            try:
                # get the message and the channel message was found in.
                parsed = getValueOrDefault(last_read[0], 'text')
                message_channel = getValueOrDefault(last_read[0], 'channel')
                if not parsed or not message_channel:
                    continue
                
                print("channel = " + message_channel)
                print("parsed = " + parsed)

                if parsed and '!foodtruck' in parsed:
                    msg = getCurrentFoodTruckInfo()
                    if not msg:
                        # TODO: show tomorrows
                        msg = "There are currently no foodtrucks open"
                    client.rtm_send_message(message_channel, msg)
            except Exception as ex:
                print("Error: " + str(ex))
