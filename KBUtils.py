import HandleConsole as con
import sys
import os
import subprocess
import json
import time
import datetime
import traceback
import eel
import clipboard
import keyboard
import base64
import win32clipboard as wcb
import wcbx
import urllib.parse
import fileWatch
import scripts
import keymacro
import clipmon
import MovieList as ML
import fernsehserien as fss

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
    "chkCR": False,
    "chkDown": False,
    "txtListEdit": "prefix1\n#prefix2\nprefix3",
    "txtDbServer": "mongodb://192.168.0.124:27017/",
    "txtMaxitems": "500",
    "txtMaxitemsize": "5000",
    "chkMovieList": False,
    "selectedDb": 1,
    "selSearchShow": "path",
    "selSearchSort": "path",
    "selSearchSort": "asc",
}

# load parameter file, always merge to xparam
fn = os.path.splitext(os.path.abspath(sys.argv[0]))[0]
fncfg = fn + ".json"
lastxp = ""

def loadParamsFile():
    global lastxp
    if os.path.exists(fncfg):
        with open(fncfg, 'r') as f1:
            x = json.load(f1)
        for k in x.keys():
            xparam[k] = x[k]
    xp = json.dumps(xparam, indent=4)
    if xp != lastxp:
        lastxp = xp
        return True
    return False

loadParamsFile()
paramsWatch = fileWatch.FileWatch(fncfg, 30)

def checkParamsFile():
    if not paramsWatch.checkFile(): return
    print(f"Params file changed, reloading...")
    if loadParamsFile():
        eel.loadParams()

def dump(o):
    print(json.dumps(o, indent=4))

@eel.expose
def saveParams(x, closing=False):
    global lastxp
    if closing: 
        cm.saveClips(cm.clips)
    for k in x.keys():
        xparam[k] = x[k]
    xp = json.dumps(xparam, indent=4)
    if xp != lastxp:
        lastxp = xp
        with open(fncfg, 'w') as f1:
            f1.write(xp)
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
    x = x.strip()
    x = scripts.text2linkAdaptLine(x)
    clipboard.copy(x)

@eel.expose
def doCmd(cmd, p=None):
    print(f'doCmd {cmd}')

    if cmd == "FromClipb":
        sendCallback("text2Link")

    if cmd == "CopyAll":
        sendMacro("CopyAll", sendCallback, "text2Link")

    if cmd == "Tele5":
        sendMacro("CopyAll", sendCallback, "tele5")

    if cmd == "Filename":
        sendCallback("filename")

def sendCallback(type):
    if type == "text2Link": eel.text2Link(scripts.text2linkIngnore(clipboard.paste()))
    if type == "tele5": eel.text2Link(scripts.tele5(clipboard.paste()))
    if type == "filename": eel.text2Link(scripts.filename(wcbx.cbText(False).strip()))


### Send keypresses #######################################

macros = { 
    "Marco1": ["alt+tab", 500, "f2", 200, "right, shift+ctrl+left, shift+left, del"],
    "Marco2": ["alt+tab", 500, "f2", 200, "right, shift+ctrl+left, shift+left, del, enter", 500, "down"],
    "CopyAll": ["alt+tab", 500, "ctrl+a, ctrl+c, ctrl+shift+home, ctrl+shift+home", 500],
    "Copy": ["alt+tab", 500, "ctrl+c", 500],
    "Undo": ["alt+tab", 500, "ctrl+z", 500],
}

km = keymacro.KeyMacro()

@eel.expose
def sendText(x):
    print(f'sendKeys {x}')
    if (x == "clipboard"): 
        x = clipboard.paste()
        x = x.replace("\n", ", ").replace("\r", "").replace("\t", " ").replace("  ", " ").strip()
    dash = " - " if xparam["chkDash"] else " "
    a = ["alt+tab", 500]
    if xparam["chkPotpl"]: 
        a = a + ["insert", 500]
    a = a + ["f2", 300]
    if xparam["chkPostfix"]: 
        a = a + ["right", f"${dash}{x}"]
    else: 
        a = a + ["home", f"${x}{dash}"]
    if xparam["chkCR"]: 
        a = a + ["enter", 500]
    if xparam["chkDown"]: 
        a = a + ["down"]
    km.send(a)

@eel.expose
def sendMacro(k, callback=None, type=""):
    print(f'sendMacro {k}')
    if k in macros.keys():
        km.send(macros[k], callback, type)


### Key definitions #######################################

fnkeys = fn + ".keys.json"
keys = {}

@eel.expose
def loadKeys():
    global keys
    try:
        if os.path.exists(fnkeys):
            with open(fnkeys, 'r') as f1:
                keys = json.load(f1)
    except:
        traceback.print_exc()
    regHotkeys(keys)
    return keys

@eel.expose
def saveKeys(keysNew):
    global keys
    dump(keysNew)
    try:
        with open(fnkeys, 'w') as f1:
            json.dump(keysNew, f1, indent=4)
    except:
        traceback.print_exc()
    unregHotkeys(keys)
    keys = keysNew
    regHotkeys(keys)

def regHotkeys(keys):
    for x in keys.values():
        try:
            if "hotkey" in x:
                keyboard.add_hotkey(x["hotkey"], doKey, [x["name"], x["mode"], x["param"]])
        except:
            traceback.print_exc()

def unregHotkeys(keys):
    for x in keys.values():
        try:
            if "hotkey" in x:
                keyboard.remove_hotkey(x["hotkey"])
        except:
            traceback.print_exc()

keyOptions = {
    "keymacro": [],
    "editclip": ["", "strip", "lower", "upper", "capwords", "urlencode", "urldecode", 
                 "b64decode", "b64encode", "totext", "time2epoch", "epoch2time"],
    "internal": ["", "bufClear", "bufAppend", "bufAppendLine", "bufCopy", 
                 "fernsehserien", "fernsehserien2", "fernsehserienSel", "fernsehserienCB"],
    "external": [],
}

@eel.expose
def loadKeyOptions():
    return keyOptions

showCbFmts = True
tFormatUi = "%d.%m.%Y %H:%M:%S"

def editClip(p, s):
    if p == "strip": s = s.strip()
    if p == "lower": s = s.lower()
    if p == "upper": s = s.upper()
    if p == "capwords": s = " ".join(w.capitalize() for w in s.split())
    if p == "urlencode": s = urllib.parse.quote(s)
    if p == "urldecode": s = urllib.parse.unquote(s)
    if p == "b64decode": s = base64.b64decode(s.encode("ascii")).decode("ascii")
    if p == "b64encode": s = base64.b64encode(s.encode("ascii")).decode("ascii")
    if p == "totext": s = wcbx.cbText(showCbFmts).strip()
    if p == "time2epoch": s = int(time.mktime(time.strptime(s, tFormatUi)))
    if p == "epoch2time": s = time.strftime(tFormatUi, time.localtime(int(s)))
    prl(f"New clipboard text:\n{s}")
    return s

internalBuf = ""

def doBuf(p):
    global internalBuf
    if p == "bufClear": internalBuf = ""
    if p == "bufAppend": internalBuf = internalBuf + " " + clipboard.paste()
    if p == "bufAppendLine": internalBuf = internalBuf + clipboard.paste() + "\n"
    if p == "bufCopy": clipboard.copy(internalBuf)

@eel.expose
def doKey(name, mode, param):
    try:
        print(f"doKey {name}, {mode}, {param}")

        if mode == "editclip":
            s = clipboard.paste()
            s = editClip(param.lower(), s)
            clipboard.copy(s)

        if mode == "keymacro":
            km.send(json.loads(param))

        if mode == "internal":
            if param.startswith("buf"): doBuf(param)
            if param == "fernsehserien": sendMacro("CopyAll", fss.sendCallback, "fernss")
            if param == "fernsehserien2": sendMacro("CopyAll", fss.sendCallback, "fernss2")
            if param == "fernsehserienSel": sendMacro("Copy", fss.sendCallback, "fernss")
            if param == "fernsehserienCB": fss.sendCallback("fernss")

    except:
        traceback.print_exc()


### Clipboard monitor #####################################

fnclips = fn + ".clips.json"
cm = clipmon.ClipMon(fnclips, xparam)
lastClip = cm.clips[len(cm.clips) - 1]["data"] if len(cm.clips) > 0 else ""
clipsWatch = fileWatch.AutoSave(fnclips, 300)

@eel.expose
def cmCopy(t):
    if t:
        x = cm.cmFind(t)
        if x: clipboard.copy(x["data"])
    else:
        clipboard.copy(cm.cmMerge())

@eel.expose
def cmSelect(t):
    x = cm.cmFind(t)
    eel.setValue("txtCliptext", x["data"])

@eel.expose
def cmInit():
    eel.clipmonUpdate(cm.renderClipmon())

def newText(s):
    cm.newText(s)
    eel.clipmonUpdate(cm.renderClipmon())
    if clipsWatch.saveNeeded(): cm.saveClips(cm.clips)


### MovileList ############################################

ML.init(xparam["txtDbServer"], xparam["selectedDb"])

@eel.expose
def mlSearch(text, fromPaste=False):
    if any(c in text for c in ["\\", "://", "<", ">"]): return
    if fromPaste: eel.movielistPaste(text)
    sort = xparam["selSearchSort"]
    sortDir = -1 if xparam["selSearchSortDir"] == "desc" else 1
    limit = int(xparam["txtSearchMaxResults"])
    res = ML.search(text, sort, sortDir, limit)
    item = xparam["selSearchShow"]
    html = ML.renderSearchResult(res, item)
    eel.movielistUpdate(html)

@eel.expose
def mlAction(a, i):
    d = ML.res[i]
    p = d["path"]
    if a == 0: clipboard.copy(p)
    if a == 1: subprocess.Popen(f'"{p}"', shell=True)
    if a == 2: subprocess.Popen(f'explorer.exe /select, "{p}"')

@eel.expose
def mlData(i):
    return ML.res[i]

@eel.expose
def mlDb(i):
    ML.init(xparam["txtDbServer"], i)
    x = {"selectedDb": i}
    saveParams(x)

#test
#ML.purgeFiles()            
#ML.updateDb("D:\\Download\\Media")

# use files for db update
if len(sys.argv) > 1:
    try:
        con.showConsole(con.conOn)
        for fx in sys.argv[1:]:
            ML.updateDb(fx)
        ML.purgeFiles()            
        input("...")
    except:
        con.showConsole(con.conOn)
        traceback.print_exc()
        input("...")
    sys.exit()


### Start UI ##############################################

def close_callback(route, websockets):
    if not websockets:
        cm.saveClips(cm.clips)
        exit()

#cmdline_args = []    
cmdline_args = ["–disable-translate", "–incognito", 
    #f"--window-position={xparam['x']},{xparam['y']}", 
    #f"--window-size={xparam['w']},{xparam['h']}"
]
eel.start('main.html', 
    mode="chrome",
    cmdline_args=cmdline_args, 
    port=xparam["port"], 
    position=(xparam["x"], xparam["y"]), 
    size=(xparam["w"], xparam["h"]),
    close_callback=close_callback,
    block=False)

# non-blocking eel reqires a loop 
# we can use it for file/clipboard monitoring/polling

while True:
    eel.sleep(1.0)  

    try: 
        # check clipboard for changes
        #clip = clipboard.paste()
        clip = wcbx.cbText()
        if clip and clip != lastClip:
            lastClip = clip
            if xparam["chkClipmon"]: newText(clip)
            if xparam["chkMovieList"]: mlSearch(clip, True)
    except:
        lastexp = traceback.format_exc()
        print(lastexp)
 
    try: 
        checkParamsFile()
    except:
        lastexp = traceback.format_exc()
        print(lastexp)
