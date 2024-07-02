import traceback
import win32clipboard as wcb

CF_HTML = 49322
CF_Filename = 49158
cbfmts = {val: x for x, val in vars(wcb).items() if x.startswith('CF_')}
res = {}

def cbFmtName(fmt):
    if fmt in cbfmts:
        return cbfmts[fmt]
    try:
        return wcb.GetClipboardFormatName(fmt)
    except:
        return "unknown"
    
def cbShowfmts(withData=False):
    fmt = 0
    p = ""
    while True:
        fmt = wcb.EnumClipboardFormats(fmt)
        if fmt == 0: break
        p = p + '{:5} ({})\n'.format(fmt, cbFmtName(fmt))
        if withData:
            try:
                p = f"{p}{str(wcb.GetClipboardData(fmt))}\n\n"
            except:
                p = p + "(cannot show data)\n\n"
    return p

def cbData(cbf, res=res):
    if wcb.IsClipboardFormatAvailable(cbf):
        res["obj"] = wcb.GetClipboardData(cbf)
        res["str"] = str(res["obj"])
        return True
    return False

def cbText(showCbFmts=False):
    wcb.OpenClipboard()
    if showCbFmts:
        print(f"Current clipboard formats:\n{cbShowfmts()}\n")

    res = {}
    if cbData(wcb.CF_HDROP, res):
        # file(s) to string
        s = res["str"]
        #print(s)
        s = s.replace("('", "").replace("',)", "").replace("')", "").replace("\\\\", "\\").replace("', '", "\n")
    elif cbData(CF_HTML, res):
        s = res["str"]
    elif cbData(wcb.CF_UNICODETEXT, res):
        s = res["str"]
    elif cbData(wcb.CF_TEXT, res):
        s = res["str"]

    wcb.CloseClipboard()
    return s


if __name__ == "__main__":
    try:
        wcb.OpenClipboard()
        print(f"Current clipboard formats:\n{cbShowfmts(True)}")
        wcb.CloseClipboard()
    except:
        traceback.print_exc()

    input("...")
