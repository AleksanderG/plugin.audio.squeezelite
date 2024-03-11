import xbmcaddon
import os
import sys
import subprocess
import requests
import json

global addon
global LOGPREFIX

class LMS:
    _host = None
    _port = None
    _playerid = None

    def __init__(self):
        self.updateConfig()

    def updateConfig(self):
        self._host = addon.getSetting("host")
        self._port = addon.getSetting("port")
        self._playerid = addon.getSetting("id")

    def power(self, cmd):
        if not (self._host == "" or self._port == "" or self._playerid == ""):
            url = "http://%s:%s/jsonrpc.js" % (self._host, self._port)
            data = { "id": 1, "method": "slim.request", "params": [self._playerid, ["power", cmd]]}
            try:
                xbmc.log(LOGPREFIX+"set power: "+str(cmd), xbmc.LOGINFO)
                requests.post(url, data=json.dumps(data))
            except:
                xbmc.log(LOGPREFIX+"server connection error", xbmc.LOGERROR)
        else:
            xbmc.log(LOGPREFIX+"check lms settings", xbmc.LOGWARNING)

class SQUEEZE:
    _host = None
    _port = None
    _executable = None
    _name = None
    _playerid = None
    _args = None

    def __init__(self):
        self.updateConfig()

    def updateConfig(self):
        self._host = addon.getSetting("host")
        self._executable = addon.getSetting("exec")
        self._name = addon.getSetting("name")
        self._playerid = addon.getSetting("id")
        self._args = addon.getSetting("args")

    def start(self):
        self.stop()
        cmd = [self._executable, "-s", self._host, "-m", self._playerid, "-n", self._name, "-M", "Kodi"] + self._args.split()

        if not (self._host == "" or self._executable == "" or self._name == "" or self._playerid == ""):
            try:
                xbmc.log(LOGPREFIX+"start squeezelite process", xbmc.LOGINFO)
                subprocess.Popen(cmd, stderr=subprocess.STDOUT)
            except:
                xbmc.log(LOGPREFIX+"start process error", xbmc.LOGERROR)
        else:
            xbmc.log(LOGPREFIX+"check squeeze settings", xbmc.LOGWARNING)

    def stop(self):
        xbmc.log(LOGPREFIX+"stop squeezelite process", xbmc.LOGINFO)
        os.system("killall squeezelite")
        xbmc.sleep(1000)

class Service(xbmc.Monitor):
    _lms = None
    _squeeze = None

    def __init__(self):
        xbmc.log(LOGPREFIX+"service started", xbmc.LOGINFO)
        self._lms = LMS()
        self._squeeze = SQUEEZE()

        self._squeeze.start()
        while not self.abortRequested():
            if self.waitForAbort(10):
                break

    def onNotification(self, sender, method, data):
        data = json.loads(data)
        if method == "Player.OnPlay":
            self._lms.power(0)
        if method == "Player.OnStop":
            self._lms.power(1)

    def onSettingsChanged(self):
        self._lms.updateConfig()
        self._squeeze.updateConfig()
        self._squeeze.start()

addon = xbmcaddon.Addon()
LOGPREFIX = "[" + addon.getAddonInfo('id') + "] "

xbmc.log(LOGPREFIX+"plugin started", xbmc.LOGINFO)
service = Service()
xbmc.log(LOGPREFIX+"plugin stopped", xbmc.LOGINFO)

