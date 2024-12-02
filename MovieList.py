import os
import sys
import datetime
import json
import re
import MovieDb as mdb

# html tag with name n, data d, attributes a
def t(n, d, a=""):
    return f"<{n} {a}>{d}</{n}>"

def init():
    mdb.dbConnect()

def search(q, limit=200):
    global res
    q = makeQuery(q)
    res = mdb.search(q, limit)
    return res

def makeQuery(s, mode="fuzzy"):
    if mode == "fuzzy":
        # replace non aplphanumerics with blank
        s = re.sub("[^0-9a-zA-Z]+", " ", s)
        # replace multiple blanks with one
        s = " ".join(s.split())
        # add a leading an trailing blank
        s = " " + s + " "
        # replace blanks win regex "any string"
        s = s.replace(" ", ".*")
        print(f"normalized regex: {s}")
        q = {"file": {"$regex": s, "$options": "i"}}
    if mode == "regex":
        q = {"file": {"$regex": s, "$options": "i"}}
    if mode == "text":
        q = {"$text": {"$search": s}}
    return q

def renderSearchResult(res):
    h = ""
    h = h + t("th", "Path", "")
    h = h + t("th", "Action", "width='80px' style='text-align:center'")
    rows = ""
    for i, x in enumerate(res):
        d = ""        
        d = d + t("td", x["path"], "")
        img = f'<img class="img1" title="copy" src="clipboard1.png" onclick="eel.mlAction(0, {i})">'
        img = img + f'<img class="img1" title="play" src="play.png" onclick="eel.mlAction(1, {i})">'
        img = img + f'<img class="img1" title="explore" src="explore.png" onclick="eel.mlAction(2, {i})">'
        d = d + t("td", img, "style='text-align:center'")
        a = f'onclick="mlDlg({i})"'
        rows = t("tr", d, a) + "\n" + rows
    rows = t("tr", h) + "\n" + rows
    html = t("table", rows, "class='movielist-table max'")
    return html    

