import time
import traceback
import keyboard
import queue
import threading

class KeyMacro:
    def __init__(self):
        self.qSend = queue.Queue()
        self.th1 = threading.Thread(target=self.worker, daemon=True)
        self.th1.start()

    def send(self, keys, callback=None, type=""):
        self.qSend.put({
            "keys": keys,
            "callback": callback,
            "type": type
        })

    def doSend(self, a):
        for x in a:
            if isinstance(x, int):
                time.sleep(x / 1000.0)
            elif x[0:1] == "$":
                keyboard.write(x[1:])
            else:
                keyboard.send(x)

    def worker(self):
        while 1:
            try:
                a = self.qSend.get()
                self.doSend(a["keys"])
                cb = a["callback"]
                if cb:
                    cb(a["type"])
            except:
                traceback.print_exc()
            time.sleep(1)


