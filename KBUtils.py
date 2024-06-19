import HandleConsole as con
import sys
import os
import json
import subprocess
import time
import traceback
import eel
import clipboard
import keyboard
import queue
import threading

eel.init('web')

# default app parameters
xparam = {
    "x": 50,
    "y": 50, 
    "w": 800,
    "h": 500,
    "port": 0,
    "chkPostfix": False,
    "chkDash": False,
    "chkPotpl": False,
    "chkClipmon": False,
    "sendMacro": { 
        "Marco1": ["alt+tab", 500, "f2", 200, "right, shift+ctrl+left, shift+left, del"],
        "Marco2": ["alt+tab", 500, "f2", 200, "right, shift+ctrl+left, shift+left, del, enter", 500, "down"],
    },
    "txtListEdit": "prefix1\nprefix2"
}

# load parameter file, always merge to xparam
fn = os.path.splitext(os.path.abspath(sys.argv[0]))[0]
fncfg = fn + ".json"
if os.path.exists(fncfg):
    with open(fncfg, 'r') as f1:
        x = json.load(f1)
    for k in x.keys():
        xparam[k] = x[k]

def dump(o):
    print(json.dumps(o, indent=4))

@eel.expose
def saveParams(x):
    for k in x.keys():
        xparam[k] = x[k]
    with open(fncfg, 'w') as f1:
        json.dump(xparam, f1, indent=4)
    return xparam

@eel.expose
def loadParams():
    dump(xparam)
    return xparam

qSend = queue.Queue()

@eel.expose
def sendText(x):
    print(f'sendKeys {x}')
    if (x == "clipboard"): x = clipboard.paste()
    dash = " - " if xparam["chkDash"] else " "
    a = ["alt+tab", 500]
    if xparam["chkPotpl"]: a = a + ["insert", 500]
    a = a + ["f2", 300]
    if xparam["chkPostfix"]: 
        a = a + ["right", f"${dash}{x}"]
    else: 
        a = a + ["home", f"${x}{dash}"]
    qSend.put(a)

@eel.expose
def sendMacro(k):
    print(f'sendMacro {k}')
    mac = xparam["sendMacro"]
    if k in mac.keys():
        qSend.put(mac[k])

def doSend(a):
    dump(a)
    for x in a:
        if isinstance(x, int):
            time.sleep(x / 1000.0)
        elif x[0:1] == "$":
            keyboard.write(x[1:])
        else:
            keyboard.send(x)
    #s = json.dumps(a)

def worker():
    while 1:
        try:
            a = qSend.get()
            doSend(a)
        except:
            traceback.print_exc()
        time.sleep(1)

th1 = threading.Thread(target=worker, daemon=True)
th1.start()


#cmdline_args = []    
cmdline_args = ["–disable-translate", "–incognito", 
    f"--window-position={xparam['x']},{xparam['y']}", 
    f"--window-size={xparam['w']},{xparam['h']}"]
eel.start('main.html', 
    cmdline_args=cmdline_args, 
    port=xparam["port"], 
    position=(xparam["x"], xparam["y"]), 
    size=(xparam["w"], xparam["h"]),
    block=False)

# non-blocking eel reqires a loop 
# we can use it for file/clipboard monitoring/polling

lastClip = ""
lastexp = None
while True:
    eel.sleep(1.0)  

    try: 
        # check clipboard for changes
        if xparam["chkClipmon"]:
            clip = clipboard.paste()
            if clip and clip != lastClip:
                #decodePaste(clip)
                lastClip = clip

    except:
        lastexp = traceback.format_exc()
        print(lastexp)
 