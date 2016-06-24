from __future__ import unicode_literals
import time
import json

class FoodTruck:
    def __init__(self, vendorName, vendorData = None, searchAddr = None):
        self.vendorName = vendorName
        self.name = ""
        self.description = ""
        self.url = ""
        self.twitter = ""
        self.likes = 0
        self.paymentMethods = []
        self.openTime = 0
        self.closeTime = 0
        self.location = ""
        self.latitude = 0
        self.longitude = 0
        self.region = ""
        self.parse(vendorData, searchAddr)


    def parse(self, vendorData, searchAddr = None):
        if not vendorData:
            return False

        self.name = vendorData["name"]
        self.description = vendorData["description_short"]
        self.region = vendorData["region"]
        self.url = vendorData["url"]
        self.twitter = vendorData["twitter"]
        self.likes = vendorData["rating"]
        self.paymentMethods = vendorData["payment_methods"]
        self._parseHoursOfOperation(vendorData["open"], searchAddr)


    def getWebsite(self):
        return "http://" + self.url


    def getStreetFoodAppUrl(self):
        return "http://streetfoodapp.com/" + self.region + "/" + self.vendorName


    def getTwitterUrl(self):
        return "https://twitter.com/" + self.twitter


    def _parseHoursOfOperation(self, openArr, searchAddr = None):
        if len(openArr) == 1:
            self._parseHoursData(openArr[0])
            return True
        # If the truck is in multiple locations find the one with the address
        if len(openArr) > 1 and searchAddr:
            for entry in openArr:
                location = entry["display"]
                if searchAddr in location:
                    self._parseHoursData(entry)
                    return True
        return False # failed to parse


    def _parseHoursData(self, data):
        self.openTime = data["start"]
        self.closeTime = data["end"]
        self.location = data["display"]
        self.latitude = data["latitude"]
        self.longitude = data["longitude"]


    def getFormattedHoursOfOperation(self):
        # startDate = time.ctime(self.openTime)
        # endDate = time.ctime(self.closeTime)
        startStruct = time.localtime(self.openTime)
        endStruct = time.localtime(self.closeTime)
        openHour = self._formatHour(startStruct.tm_hour)
        closeHour = self._formatHour(endStruct.tm_hour)
        return openHour + " - " + closeHour


    def getFormattedOperationDate(self):
        startStruct = time.localtime(self.openTime)
        return time.strftime("%A, %B %d %Y", startStruct)


    def _formatHour(self, hour):
        meridian = "AM"
        if hour > 12:
            meridian = "PM"
        hour12 = hour % 12
        return str(hour12) + meridian


    def isOpen(self):
        localTimeSeconds = time.localtime()
        return (localTimeSeconds >= self.openTime and localTimeSeconds < self.closeTime)


    def getFormattedPaymentMethods(self):
        if not self.paymentMethods or len(self.paymentMethods) == 0:
            return ""
        formattedMethods = []
        for method in self.paymentMethods:
            fmethod = method.replace("_", " ").title()
            formattedMethods.append(fmethod)
        return ", ".join(formattedMethods)