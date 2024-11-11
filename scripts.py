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


def text2linkIngnore(text, ign):
    res = []
    for x in text.splitlines():
        if not any(x1 in x for x1 in ign):
            res.append(x)
    return "\n".join(res)


def tele5(text):
    # text is copied from https://tele5.de/
    s = ""
    res = re.findall(r"\r\nx\r\n([^\r\n]*)\r\n", text)

    ignore = ["Star Trek", "Ruhelose Seelen", "Raumschiff Enterprise", "Relic Hunter", "Arabellas Crime Time"]

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

