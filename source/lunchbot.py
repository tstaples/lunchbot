# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import util
import streetfoodapp as sfa
from slackclient import SlackClient
from foodtruck import FoodTruck
from config import LunchbotConfig


##################################################################

if __name__ == "__main__":
    config = LunchbotConfig()
    client = SlackClient(config.api_key)

    if not client.rtm_connect():
        print("Failed to connect to Slack")
        exit(1)

    while True:
        time.sleep(1)
        last_read = client.rtm_read()
        if last_read:
            try:
                # get the message and the channel message was found in.
                parsed = util.getValueOrDefault(last_read[0], 'text')
                message_channel = util.getValueOrDefault(last_read[0], 'channel')
                if not parsed or not message_channel:
                    continue
                
                print("channel = " + message_channel)
                print("parsed = " + parsed)

                if parsed and '!foodtruck' in parsed:
                    msg = sfa.getCurrentFoodTruckInfo(config.region)
                    if not msg:
                        # TODO: show tomorrows
                        msg = "There are currently no foodtrucks open"
                    client.rtm_send_message(message_channel, msg)
            except Exception as ex:
                print("Error: " + str(ex))
