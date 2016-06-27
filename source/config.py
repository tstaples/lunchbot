from __future__ import unicode_literals
import ConfigParser
import os
import sys
import inspect


class LunchbotConfig:
    def __init__(self):
        self.env = self._parseEnv(sys.argv, ["development", "production"])
        self.config = self._readConfig(self.env)        
        self.api_key = self.config.get("API Tokens", "token")
        self.region = self.config.get("Region", "region")


    def _readConfig(self, env):
        config = ConfigParser.ConfigParser()
        path = self._getConfigFilePath("lunchbot", env)
        try:
            config.readfp(open(path))
        except ConfigParser.ParsingError as ex:
            print("Error reading config file '%s': %s" % (path, str(ex)))
        return config


    def _getConfigPath(self):
        return self.getRootDir() + "/config"


    def _getConfigFilePath(self, prefix, env):
        return self._getConfigPath() + "/" + prefix + "-" + env + ".cfg"


    def getRootDir(self):
        return os.path.abspath(os.path.dirname(sys.argv[0]) + "/..")


    def getCurrentDir():
        return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


    def _parseEnv(self, args, validEnvs):
        env = "development"
        if len(args) == 1:
            return env

        inEnv = args[1]
        if inEnv in validEnvs:
            env = inEnv
        else:
            print("Warning: %s is not a valid environment. Using development by default")
        return env