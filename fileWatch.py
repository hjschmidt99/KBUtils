import sys
import os
import json
import subprocess
import time
import datetime
import traceback

class AutoSave:
    def __init__(self, name, interval=600):
        self.name = name
        self.td = interval
        self.nextSave = int(time.time()) + self.td

    def saveNeeded(self):
        t0 = time.time()
        if int(t0) < self.nextSave: return False
        self.nextSave = int(t0) + self.td
        print(f"{datetime.datetime.now()} AutoSave: save needed for {self.name}")
        return True
    
    