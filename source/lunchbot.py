# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import os
import sys
import json
import requests
import ConfigParser
from slackclient import SlackClient
from foodtruck import FoodTruck
from config import LunchbotConfig


def readFirstLineOfFile(path):
    text = None
    try:
        f = open(path, "r")
        text = f.read()
        f.close()
    except Exception as ex:
        print("Error reading file: " + str(ex))
    return text


def getSchedule(region):
    rjson = None
    try:
        response = requests.get("http://data.streetfoodapp.com/1.1/schedule/" + region)
        rjson = response.json()
        #rjson = json.load(open("response.json", "r")) # temp for testing so we don't spam requests
    except Exception as ex:
        print("Error getting schedule for region '%s': %s" % (region, str(ex)))
    return rjson


def getRegionName(rjson, region):
    regionDisplayName = region
    metadata = getValueOrDefault(rjson, "metadata")
    if not metadata:
        return regionDisplayName

    regions = getValueOrDefault(metadata, "regions")
    if not regions or len(regions) == 0:
        print("Response had no region information")
    else:
        regionDisplayName = regions[0]["name"]
    return regionDisplayName


def getFoodTrucks(region):
    # TODO: cache response and expire once per day
    rjson = getSchedule(region)
    if not rjson:
        return []

    # Get the full display name of the region
    regionDisplayName = getRegionName(rjson, region)

    foodTrucks = []
    vendorsObj = rjson["vendors"]
    for vendorName in vendorsObj:
        foodTruck = FoodTruck(vendorName, vendorsObj[vendorName], regionDisplayName)
        foodTrucks.append(foodTruck)
    return foodTrucks


def getTodaysFoodTruck(region):
    foodtrucks = getFoodTrucks(region)
    for foodtruck in foodtrucks:
        if foodtruck.isOpen():
            return foodtruck
    #return None
    return foodtrucks[0] # temp for testing


def boldText(txt):
    return "*" + txt + "*"


def getCurrentFoodTruckInfo(region):
    foodtruck = getTodaysFoodTruck(region)
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

if __name__ == "__main__":
    config = LunchbotConfig()
    client = SlackClient(config.api_key)

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
                        msg = getCurrentFoodTruckInfo(config.region)
                        if not msg:
                            # TODO: show tomorrows
                            msg = "There are currently no foodtrucks open"
                        client.rtm_send_message(message_channel, msg)
                except Exception as ex:
                    print("Error: " + str(ex))
