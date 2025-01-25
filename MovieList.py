import re
import MovieDb as mdb
import datetime

# html tag with name n, data d, attributes a
def t(n, d, a=""):
    return f"<{n} {a}>{d}</{n}>"

def init(i):
    mdb.collectionName = f"files{i}"
    mdb.dbConnect()

def search(q, sort, sortDir, limit):
    global res
    q = makeQuery(q)
    res = mdb.search(q, sort, sortDir, limit)
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

def renderSearchResult(res, item="path"):
    h = ""
    h = h + t("th", f"Path ({len(res)} results)", "")
    h = h + t("th", "Action", "width='80px' style='text-align:center'")
    rows = ""
    for i, x in enumerate(res):
        d = ""        
        d = d + t("td", x[item], "class='wrapword'")
        img = f'<img class="img1" title="copy" src="clipboard1.png" onclick="eel.mlAction(0, {i})">'
        img = img + f'<img class="img1" title="play" src="play.png" onclick="eel.mlAction(1, {i})">'
        img = img + f'<img class="img1" title="explore" src="explore.png" onclick="eel.mlAction(2, {i})">'
        d = d + t("td", img, "style='text-align:center'")
        a = f'onclick="mlDlg({i})"'
        rows = rows + "\n" + t("tr", d, a)
    rows = t("tr", h) + rows + "\n"
    html = t("table", rows, "class='movielist-table max'")
    return html    

def updateDb(txtFileOrFolder):
    print(f"db update ({mdb.coll}) from {txtFileOrFolder}")
    t0 = datetime.datetime.now()
    mdb.addMany(txtFileOrFolder)
    t1 = datetime.datetime.now()
    print(f"db update done in {t1 - t0}")

def purgeFiles():
    mdb.purgeFiles()

