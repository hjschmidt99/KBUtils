import sys
import os
import json
import subprocess
import time
import datetime
import traceback
import clipboard
import threading
import urllib.parse
import re


def text2linkAdaptLine(x):
    t1 = "RELOAD "
    if x.upper().startswith(t1):
        x = x[len(t1):]
        if x.endswith("m"):
            x = x[:-1]
    return x


def text2linkIngnore(text):
    ign = ["small screenshot"]
    res = []
    for x in text.splitlines():
        if not any(x1 in x for x1 in ign):
            res.append(x)
    return "\n".join(res)


def tele5(text):
    # text is copied from https://tele5.de/
    s = ""
    res = re.findall(r"\r\nx\r\n([^\r\n]*)\r\n", text)

    ignore = ["Star Trek", "Ruhelose Seelen", "Raumschiff Enterprise", "Relic Hunter", "Arabellas Crime Time",
              "In Search of Darkness", "Eli Roth's GHOSTS", "Robin Hood -", "Doctor Who -", "Holzer Files - "]

    for x in res:
        print(x)
        if not x.startswith(tuple(ignore)):
            # titles can be doubled, remove one
            a = x.split(" - ")
            al = len(a)
            if al == 2:
                if (a[0] == a[1]): 
                    x = a[0]
            if al == 4:
                if (a[0] == a[2]): 
                    x = a[2] + " - " + a[3]
            s = f"{s}\n{x}"

    return s


def filename(text):
    res = []
    for x in text.splitlines():
        p1, f1 = os.path.split(x)
        f2, ex2 = os.path.splitext(f1)
        f2 = f2.replace(" (crop)", "").replace(" (4-3)", "")
        res.append(f2)
    return "\n".join(res)

