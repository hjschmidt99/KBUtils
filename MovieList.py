import os
import sys
import datetime
import json
import MovieDb as mdb

# html tag with name n, data d, attributes a
def t(n, d, a=""):
    return f"<{n} {a}>{d}</{n}>"

def init():
    mdb.dbConnect()

def search(q, limit=200):
    global res
    q = mdb.makeQuery(q)
    res = mdb.search(q, limit)
    return res

def renderSearchResult(res):
    h = ""
    h = h + t("th", "Path", "")
    h = h + t("th", " ", "width='10px' style='text-align:center'")
    rows = ""
    for i, x in enumerate(res):
        d = ""        
        d = d + t("td", x["path"], "class='tdtruncate'")
        img = f'<img class="img1" title="copy" src="clipboard1.png" onclick="eel.mlCopy({i})">'
        d = d + t("td", img, "style='text-align:center'")
        a = f'onclick="mlDlg({i})"'
        rows = t("tr", d, a) + "\n" + rows
    rows = t("tr", h) + "\n" + rows
    html = t("table", rows, "class='movielist-table max'")
    return html    

