# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import util
import streetfoodapp as sfa
from slackclient import SlackClient
from foodtruck import FoodTruck
from config import LunchbotConfig
import commands

##################################################################

def buildCommands():
    cmds = dict()
    cmds["foodtruck"] = commands.CurrentFoodTruck(config)
    return cmds


def runCommand(msg, cmds):
    ret = None
    if msg and len(msg) > 1 and msg[0] == "!":
        args = msg.split(" ")
        cmd = args.pop(0)[1:]
        if cmd in cmds:
            print("running command: %s" % cmd)
            ret = cmds[cmd].run(args)
    return ret

##################################################################

if __name__ == "__main__":
    config = LunchbotConfig()
    client = SlackClient(config.api_key)

    cmds = buildCommands()

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

                msg = runCommand(parsed, cmds)
                if msg:
                    client.rtm_send_message(message_channel, msg)

            except Exception as ex:
                print("Error: " + str(ex))
