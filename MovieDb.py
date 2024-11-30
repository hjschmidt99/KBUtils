import os
import os.path
import sys
import datetime
import glob
import json
import re
import pymongo

connStr = "mongodb://localhost:27017/"
dbName = "db"
collectionName = "files"
indexedField = "file"
extFilter = [".ts", ".mp4", ".mpg", ".vob", ".avi"]

def dbConnect():
    global client, db, coll
    client = pymongo.MongoClient(connStr)
    db = client[dbName]
    coll = db[collectionName]
    if indexedField + "_text" not in coll.list_indexes():
        coll.create_index({indexedField: "text"})

def dbItem(path, extFilter):
    p1, f1 = os.path.split(path)
    f2, ex2 = os.path.splitext(f1)
    if not ex2.lower() in extFilter: return None
    o1 = {
        #"_id": uuid.uuid4(),
        "path": path,
        "file": f2,
        "ext": ex2,
    }
    if os.path.isfile(path):
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
        o1.update({ 
            "size": size,
            "modified": mtime
        })
    return o1

def addFile(fn1):
    x1 = coll.find_one({"path": fn1})
    if not x1:
        x2 = dbItem(fn1, extFilter)
        if x2:
            print(fn1)
            coll.insert_one(x2)

def addMany(src):
    if os.path.isfile(src):
        # text file with list of files
        with open(src) as f:
            files = f.readlines()
        for fn1 in files:
            addFile(fn1.strip())
    elif os.path.exists(src):
        # recurse directory live
        for fn1 in glob.iglob(os.path.join(src, "**", "**"), recursive=True):
            addFile(fn1)

def search(q, limit=200, remove_id=True):
    cursor = coll.find(q, limit=limit)
    res = []
    for x in cursor:
        if remove_id: del x["_id"]
        res.append(x)
    print(json.dumps(res, indent=4))
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

if __name__ == "__main__":
    dbConnect()

    if len(sys.argv) > 1:
        t0 = datetime.datetime.now()
        for x1 in sys.argv[1:]:
            addMany(x1)
        t1 = datetime.datetime.now()
        print(f"done in {t1 - t0}")

    else:
        #addMany(r"D:\Data\Text\Video33.txt")
        qr = "infin y ei"
        qr = "Stargirl     Teil "
        q = makeQuery(qr)
        search(q)

    if not "debugSession" in os.environ.keys(): input("...")
