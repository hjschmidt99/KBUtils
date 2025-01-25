import sys
import os
import json
import time
import datetime
import traceback
import win32clipboard as wcb


# html tag with name n, data d, attributes a
def t(n, d, a=""):
    return f"<{n} {a}>{d}</{n}>"

class ClipMon:
    def __init__(self, fnclips, xparam):
        self.clips = []
        self.fnclips = fnclips
        self.xparam = xparam
        self.clips = self.loadClips()

    def loadClips(self):
        try:
            if os.path.exists(self.fnclips):
                with open(self.fnclips, 'r') as f1:
                    return json.load(f1)
        except:
            traceback.print_exc()
        return []

    def saveClips(self, clips):
        try:
            with open(self.fnclips, 'w') as f1:
                json.dump(clips, f1, indent=2)
        except:
            traceback.print_exc()

    def renderClipmon(self):
        h = ""
        h = h + t("th", "Text", "")
        h = h + t("th", "Size", "width='32px'")
        h = h + t("th", "Time", "width='140px'")
        i = '<img class="img1" title="merge all" src="clipboard1.png" onclick="eel.cmCopy(\'\')">'
        h = h + t("th", i, "width='10px' style='text-align:center'")
        rows = ""
        for x in self.clips:
            d = ""        
            d = d + t("td", x["name"], "class='tdtruncate'")
            d = d + t("td", x["size"])
            d = d + t("td", x["time"])
            i = '<img class="img1" title="copy" src="clipboard1.png" onclick="eel.cmCopy(\'' + x["time"] + '\')">'
            d = d + t("td", i, "style='text-align:center'")
            a = 'onclick="eel.cmSelect(\'' + x["time"] + '\')"'
            rows = t("tr", d, a) + "\n" + rows
        rows = t("tr", h) + "\n" + rows
        html = t("table", rows, "class='clipmon-table max'")
        return html    

    def cmFind(self, t):
        for x in self.clips:
            if x["time"] == t: return x;
        return None

    def cmMerge(self):
        s = "\n".join([x["data"] for x in self.clips])
        return s

    def getxparam(self, name, default):
        v = default
        try: v = int(self.xparam[name])
        except: self.xparam[name] = str(default)
        return v

    def newText(self, s):
        #print(s)
        maxTextLen = 2000
        maxClips = 200
        maxTextLen = self.getxparam("txtMaxitemsize", maxTextLen)
        maxClips = self.getxparam("txtMaxitems", maxClips)

        if len(s) > maxTextLen: return

        n = s.splitlines()[0]
        for c in "<>": n = n.replace(c, f"&#{ord(c)}")
        x = {
            "time": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "size": len(s),
            "name": n,
            "data": s
        }
        self.clips.append(x)
        if len(self.clips) > maxClips: self.clips = self.clips[1:]

