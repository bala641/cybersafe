Set objShell = CreateObject("WScript.Shell")
strPath = objShell.CurrentDirectory
' Launch Python with visible window (style 1 = normal visible window)
objShell.Run "python main.py --gui", 1, False
