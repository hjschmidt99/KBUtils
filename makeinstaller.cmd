pyinstaller.exe --onefile --noconsole ^
    --add-data="web;web" ^
    KBUtils.py
::copy /y StreamRec.cmd dist\streamrec.cmd
pause