import HandleConsole as con
import sys
import os
import json
import subprocess
import time
import datetime
import traceback
import eel
import clipboard
import keyboard
import queue
import threading
import base64

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
    "chkDown": False,
    "txtListEdit": "prefix1\n#prefix2\nprefix3",
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
def saveParams(x, closing=False):
    if closing: 
        saveClips(clips)
    for k in x.keys():
        xparam[k] = x[k]
    with open(fncfg, 'w') as f1:
        json.dump(xparam, f1, indent=4)
    return xparam

@eel.expose
def loadParams(first=False):
    dump(xparam)
    return xparam

@eel.expose
def prl(s):
    print(s)
    eel.prl(s)

@eel.expose
def prt(s):
    x = time.strftime("%H:%M:%S") + " " + s
    prl(x)

@eel.expose
def copy(x):
    clipboard.copy(x)

@eel.expose
def doCmd(cmd, p=None):
    print(f'doCmd {cmd}')

    if cmd == "FromClipb":
        qSend.put("text2Link")

    if cmd == "CopyAll":
        sendMacro("CopyAll")
        qSend.put("text2Link")


### Send keypresses #######################################

macros = { 
    "Marco1": ["alt+tab", 500, "f2", 200, "right, shift+ctrl+left, shift+left, del"],
    "Marco2": ["alt+tab", 500, "f2", 200, "right, shift+ctrl+left, shift+left, del, enter", 500, "down"],
    "CopyAll": ["alt+tab", 500, "ctrl+a, ctrl+c, ctrl+shift+home, ctrl+shift+home"],
}

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
    if xparam["chkDown"]: 
        a = a + ["enter", 500, "down"]
    qSend.put(a)

@eel.expose
def sendMacro(k):
    print(f'sendMacro {k}')
    if k in macros.keys():
        qSend.put(macros[k])

def sendArray(a):
    qSend.put(a)

def doSend(a):
    dump(a)
    for x in a:
        if isinstance(x, int):
            time.sleep(x / 1000.0)
        elif x[0:1] == "$":
            keyboard.write(x[1:])
        else:
            keyboard.send(x)

def worker():
    while 1:
        try:
            a = qSend.get()
            if isinstance(a, list):
                doSend(a)
            if isinstance(a, str):
                if a == "text2Link": eel.text2Link(clipboard.paste())
        except:
            traceback.print_exc()
        time.sleep(1)

th1 = threading.Thread(target=worker, daemon=True)
th1.start()


### Key definitions #######################################

fnkeys = fn + ".keys.json"

@eel.expose
def loadKeys():
    try:
        if os.path.exists(fnkeys):
            with open(fnkeys, 'r') as f1:
                return json.load(f1)
    except:
        traceback.print_exc()
    return {}

@eel.expose
def saveKeys(keys):
    dump(keys)
    try:
        with open(fnkeys, 'w') as f1:
            json.dump(keys, f1, indent=2)
    except:
        traceback.print_exc()

def editClip(p, s):
    if p == "lower": s = s.lower()
    if p == "upper": s = s.upper()
    if p == "capitalize": s = s.capitalize()
    if p == "b64decode": s = base64.b64decode(s.encode("ascii")).decode("ascii")
    if p == "b64encode": s = base64.b64encode(s.encode("ascii")).decode("ascii")
    return s

@eel.expose
def doKey(name, mode, param):
    try:
        print(f"doKey {name}, {mode}, {param}")

        if mode == "editclip":
            s = clipboard.paste()
            s = editClip(param.lower(), s)
            clipboard.copy(s)

        if mode == "keymacro":
            sendArray(json.loads(param))

    except:
        traceback.print_exc()


### Clipboard monitor #####################################

clips = []
maxTextLen = 2000
maxNameLen = 30
maxClips = 200
fnclips = fn + ".clips.json"

def loadClips():
    try:
        if os.path.exists(fnclips):
            with open(fnclips, 'r') as f1:
                return json.load(f1)
    except:
        traceback.print_exc()
    return []

def saveClips(clips):
    try:
        with open(fnclips, 'w') as f1:
            json.dump(clips, f1, indent=2)
    except:
        traceback.print_exc()

clips = loadClips()
lastClip = clips[len(clips) - 1]["data"]

# html tag with name n, data n, attributes a
def t(n, d, a=""):
    return f"<{n} {a}>{d}</{n}>"

@eel.expose
def renderClipmon():
    h = ""
    h = h + t("th", "Name", "")
    h = h + t("th", "Size", "width='32px'")
    h = h + t("th", "Time", "width='140px'")
    h = h + t("th", " ", "width='10px'")
    rows = ""
    for x in clips:
        d = ""        
        d = d + t("td", x["name"])
        d = d + t("td", x["size"])
        d = d + t("td", x["time"])
        i = '<img class="img1" title="copy" src="clipboard1.png" onclick="eel.cmCopy(\'' + x["time"] + '\')">'
        d = d + t("td", i, "style='text-align:center'")
        a = 'onclick="eel.cmSelect(\'' + x["time"] + '\')"'
        rows = t("tr", d, a) + "\n" + rows
    rows = t("tr", h) + "\n" + rows
    html = t("table", rows, "class='max clipmon-table'")
    return html    

def cmFind(t):
    for x in clips:
        if x["time"] == t: return x;
    return None

@eel.expose
def cmCopy(t):
    x = cmFind(t)
    if x: clipboard.copy(x["data"])

@eel.expose
def cmSelect(t):
    x = cmFind(t)
    eel.setValue("txtCliptext", x["data"])

@eel.expose
def cmInit():
    eel.clipmonUpdate(renderClipmon())

def newText(s):
    global clips
    #print(s)
    if len(s) > maxTextLen: return

    n = s if len(s) < maxNameLen else s[:maxNameLen] + "..."
    for c in "<>\"\'": n = n.replace(c, "_")
    x = {
        "time": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "size": len(s),
        "name": n,
        "data": s
    }
    clips.append(x)
    if len(clips) > maxClips: clips = clips[1:]
    eel.clipmonUpdate(renderClipmon())


### Start UI ##############################################

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

while True:
    eel.sleep(1.0)  

    try: 
        # check clipboard for changes
        if xparam["chkClipmon"]:
            clip = clipboard.paste()
            if clip and clip != lastClip:
                newText(clip)
                lastClip = clip

    except:
        lastexp = traceback.format_exc()
        print(lastexp)
 