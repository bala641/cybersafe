Set objShell = CreateObject("WScript.Shell")
strPath = objShell.CurrentDirectory
' Launch Python with NO console window (pythonw = Python without console)
' Style 0 = hidden window (no console), False = don't wait for completion
objShell.Run "pythonw main.py --gui", 0, False
