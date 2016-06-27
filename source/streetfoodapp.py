from __future__ import unicode_literals
import time
import os
import sys
import json
import requests
import util
from foodtruck import FoodTruck

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
    metadata = util.getValueOrDefault(rjson, "metadata")
    if not metadata:
        return regionDisplayName

    regions = util.getValueOrDefault(metadata, "regions")
    if not regions or len(regions) == 0:
        print("Response had no region information")
    else:
        regionDisplayName = regions[0]["name"]
    return regionDisplayName


def getFoodTrucks(region):
    # TODO: cache response and expire once per day
    foodTrucks = []
    rjson = getSchedule(region)
    if not rjson:
        return foodTrucks

    # Get the full display name of the region
    regionDisplayName = getRegionName(rjson, region)

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
