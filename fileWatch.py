import sys
import os
import json
import subprocess
import time
import datetime
import traceback

debug = False

class AutoSave:
    def __init__(self, name, interval=600):
        self.name = name
        self.td = interval
        self.nextSave = int(time.time()) + self.td

    def saveNeeded(self):
        t0 = time.time()
        if int(t0) < self.nextSave: return False
        self.nextSave = int(t0) + self.td
        if debug: print(f"{datetime.datetime.now()} AutoSave: save needed for {self.name}")
        return True
    
class FileWatch: 
    def __init__(self, fname, interval=60):
        self.fname = fname
        self.td = interval
        self.nextCheck = int(time.time()) + self.td
        self.lastMod = os.path.getmtime(fname) if os.path.exists(fname) else 0

    def checkFile(self):
        t0 = time.time()
        if int(t0) < self.nextCheck: return False
        self.nextCheck = int(t0) + self.td
        if not os.path.exists(self.fname): return False
        currentMod = os.path.getmtime(self.fname)
        if currentMod <= self.lastMod: return False
        self.lastMod = currentMod
        return True
            
       
    