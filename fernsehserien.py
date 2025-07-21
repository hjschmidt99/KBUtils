import sys
import os 
import traceback
import json
import clipboard
import re

lasttitle = "fernsehserien"

def parseTitle(t):
    global lasttitle
    re2 = r"fernsehserien\.de Logo\sfernsehserien.de\s(.*)"
    pattern2 = re.compile(re2, re.IGNORECASE)
    res2 = pattern2.findall(t)
    title = lasttitle if len(res2) == 0 else res2[0]
    lasttitle = title
    return title

def parseEvents1a(t, title):
    # Di. 03.06.2025 20:15–21:05\nVOXup\n136 a 7.07 a Ab durch den Abwasserkanal
    # 0   1  2  3    4     4      6      7   8 9 10 11 12
    re1 = r"(.{2}\.) (\d{2}).(\d{2}).(\d*) (\d{2}:\d{2}).(\d{2}:\d{2})\s*(.*)\s"
    re1 += r"(\d+)\s?([a-z]?) (\d+)\.(\d+)\s?([a-z]?)\s(.*)"
    pattern1 = re.compile(re1, re.IGNORECASE)
    res1 = pattern1.findall(t)

    s = json.dumps(res1, indent=4)
    print(s)
    print(len(res1))

    chan = ""
    a = ""
    for x in res1:
        if not chan and x[6]: chan = x[6]
        s = f"{x[0]} {x[1]}.{x[2]}.{x[3]} {x[4]}-{x[5]} - {chan} - {title} "
        s += f"s{int(x[9]):02d}e{int(x[10]):03d}{x[11]} {x[7]}{x[8]}. {x[12]}"
        a += s + "\r\n"
    return a

def parseEvents1(t, title):
    # Di. 03.06.2025 20:15–21:05\nVOXup\n136 a 7.07 a Ab durch den Abwasserkanal
    # 0                           1      2   3 4 5  6 7
    re1 = r"(.{2}\. \d{2}.\d{2}.\d* \d{2}:\d{2}.\d{2}:\d{2})\s*(.*)\s"
    re1 += r"(\d+)\s?([a-z]?) (\d+)\.(\d+)\s?([a-z]?)\s(.*)"
    pattern1 = re.compile(re1, re.IGNORECASE)
    res1 = pattern1.findall(t)

    s = json.dumps(res1, indent=4)
    print(s)
    print(len(res1))

    chan = ""
    a = ""
    for x in res1:
        if not chan and x[1]: chan = x[1]
        s = f"{x[0]} - {chan} - {title} "
        s += f"s{int(x[4]):02d}e{int(x[5]):03d}{x[6]} {x[2]}{x[3]}. {x[7]}"
        s = s.removesuffix(" NEU")
        a += s + "\r\n"
    return a

def parseEvents2(t, title):
    # Di. 03.06.2025 20:15–21:05\nVOXup\n136 Ab durch den Abwasserkanal
    # 0                           1      2   3
    re1 = r"(.{2}\. \d{2}.\d{2}.\d* \d{2}:\d{2}.\d{2}:\d{2})\s*(.*)\s"
    re1 += r"(\d+)\s(.*)"
    pattern1 = re.compile(re1, re.IGNORECASE)
    res1 = pattern1.findall(t)

    s = json.dumps(res1, indent=4)
    print(s)
    print(len(res1))

    chan = ""
    a = ""
    for x in res1:
        if not chan and x[1]: chan = x[1]
        s = f"{x[0]} - {chan} - {title} "
        s += f"{x[2]}. {x[3]}"
        s = s.removesuffix(" NEU")
        a += s + "\r\n"
    return a

def parseEvents2a(t, title):
    # Di. 03.06.2025 20:15–21:05\nVOXup\n136 Ab durch den Abwasserkanal
    # 0   1  2  3    4     4      6      7   8
    re1 = r"(.{2}\.) (\d{2}).(\d{2}).(\d*) (\d{2}:\d{2}).(\d{2}:\d{2})\s*(.*)\s"
    re1 += r"(\d+)\s(.*)"
    pattern1 = re.compile(re1, re.IGNORECASE)
    res1 = pattern1.findall(t)

    s = json.dumps(res1, indent=4)
    print(s)
    print(len(res1))

    chan = ""
    a = ""
    for x in res1:
        if not chan and x[6]: chan = x[6]
        s = f"{x[0]} {x[1]}.{x[2]}.{x[3]} {x[4]}-{x[5]} - {chan} - {title} "
        s += f"{x[7]}. {x[8]}"
        a += s + "\r\n"
    return a

def parse(t, mode=1):
    t = t.replace("\r", "")
    title = parseTitle(t)
    if mode == 1: a = parseEvents1(t, title)
    if mode == 2: a = parseEvents2(t, title)
    return a

def sendCallback(type):
    #todo: use type for different regex
    if type == "fernss": clipboard.copy(parse(clipboard.paste(), 1))
    if type == "fernss2": clipboard.copy(parse(clipboard.paste(), 2))

if __name__ == "__main__":
    try:
        t = clipboard.paste()
        a = parse(t)
        print(a)
        clipboard.copy(a)

    except:
        traceback.print_exc()
        input("...")

    #input("...")
