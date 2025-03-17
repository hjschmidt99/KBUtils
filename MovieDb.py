import os
import os.path
import sys
import datetime
import glob
import json
import pymongo

connStr = "mongodb://localhost:27017/"
dbName = "db"
collectionName = "files1"
indexedField = "file"
extFilter = [".ts", ".mp4", ".mpg", ".vob", ".avi", ".wmv", ".mpeg", ".flv", ".asf"]
client = None

def dbConnect():
    global client, db, coll, roots
    roots = []
    if client: client.close()
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

def checkRoot(fn1):
    a = fn1.lower().split("\\")
    root = a[1]
    if root in roots: return True
    roots.append(root)
    q = {"path": {"$regex": f".\\:\\\\{root}\\\\.*", "$options": "i"}}
    cursor = coll.find(q, limit=1)
    for x in cursor:
        return True
    res = input(f"\nroot folder '{root}' not yet in current DB! Continue? [y|N]").strip().lower()
    if res == "y":
        return True
    return False

def addFile(fn1):
    x1 = coll.find_one({"path": fn1})
    if not x1:
        if not checkRoot(fn1):
            #return False
            # for now do a hard exit
            sys.exit()
        x2 = dbItem(fn1, extFilter)
        if x2:
            print(fn1)
            coll.insert_one(x2)
    return True

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

def search(q, sort, sortDir, limit, remove_id=True):
    cursor = coll.find(q)
    if sort != "": cursor = cursor.sort(sort, sortDir)
    if limit > 0: cursor = cursor.limit(limit)
    res = []
    for x in cursor:
        if remove_id: del x["_id"]
        res.append(x)
    print(json.dumps(res, indent=4))
    return res

def purgeFiles():
    print(f"purging files in DB ({collectionName})")
    t0 = datetime.datetime.now()
    # find files with size
    q = {"size": {"$gt": 0}}
    cursor = coll.find(q)
    rem = []
    n = 0
    for x in cursor:
        n = n + 1
        path = x["path"]
        # is root dir available?
        a = path.split("\\")
        root = f"{a[0]}\\{a[1]}"
        if os.path.exists(root):
            # does file still exist?
            if not os.path.isfile(path):
                print(f"remove: {path}")
                rem.append(x["_id"])
        else:
            print(f'root not available: {path}')
    for rx in rem:
        coll.delete_one({"_id": rx})
    t1 = datetime.datetime.now()
    print(f"purged {len(rem)} files of {n} db entries in {t1 - t0} sec")

if __name__ == "__main__":
    dbConnect()

    if len(sys.argv) > 1:
        t0 = datetime.datetime.now()
        for x1 in sys.argv[1:]:
            addMany(x1)
        t1 = datetime.datetime.now()
        print(f"addMnay done in {t1 - t0}")
        purgeFiles()

    else:
        #addMany(r"D:\Data\Text\Video33.txt")
        s = "Stargirl"
        q = {"$text": {"$search": s}}
        search(q)

    if not "debugSession" in os.environ.keys(): input("...")
