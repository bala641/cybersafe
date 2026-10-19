# CyberSafe Launch Guide

## 🚀 Launch Options

CyberSafe provides multiple ways to launch the application with **NO console window**:

---

## ✅ **Recommended: Hidden Launch (No Console)**

### **Option 1: VBS Launcher (Best)**
Double-click: `launcher.vbs`

**What it does:**
- Launches CyberSafe GUI
- **NO Python console window appears**
- Runs completely in background
- Only GUI window is visible

### **Option 2: Hidden Batch File**
Double-click: `LAUNCH_HIDDEN.bat`

**What it does:**
- Calls the VBS launcher
- Exits immediately (no window flash)
- Completely hidden background execution

### **Option 3: START.bat (Updated)**
Double-click: `START.bat`

**What it does:**
- Uses `pythonw` (Python without console)
- No console window
- Background execution

---

## 🖥️ **Desktop Shortcut**

### **Create a Hidden Launch Shortcut:**

1. Double-click: `CREATE_SHORTCUT.bat`
2. A "CyberSafe" icon appears on your Desktop
3. Double-click the Desktop icon anytime

**Result:** CyberSafe opens with **NO console window**

---

## 🔧 **How It Works**

### **pythonw vs python:**
- `python` = Shows console window (CMD prompt)
- `pythonw` = **NO console window** (background only)

### **VBS Launcher:**
```vbs
objShell.Run "pythonw main.py --gui", 0, False
```
- `pythonw` = No console
- `0` = Hidden window style
- `False` = Don't wait for completion

---

## 📋 **Launch Methods Comparison**

| Method | Console Window | Best For |
|--------|---------------|----------|
| `launcher.vbs` | ❌ None | ✅ **Recommended** |
| `LAUNCH_HIDDEN.bat` | ❌ None | ✅ Clean launch |
| `START.bat` | ❌ None | ✅ Quick launch |
| `python main.py --gui` | ✅ Visible | ❌ Development only |
| Desktop Shortcut | ❌ None | ✅ **Best UX** |

---

## 🎯 **Quick Start**

**For regular users:**
1. Run `CREATE_SHORTCUT.bat` once
2. Use Desktop shortcut forever
3. No console ever appears! ✨

**For developers:**
- Use `python main.py --gui` to see console output for debugging

---

## ⚙️ **Technical Details**

### **Files Updated:**
- `launcher.vbs` - Uses `pythonw` with hidden style
- `START.bat` - Uses `pythonw` instead of `python`
- `CREATE_SHORTCUT.bat` - Points to VBS launcher
- `LAUNCH_HIDDEN.bat` - New dedicated hidden launcher

### **Python Executable:**
- `pythonw.exe` is included with all Python installations
- Located in same directory as `python.exe`
- Specifically designed for GUI applications

---

## 🔍 **Troubleshooting**

**Q: I don't see any window at all?**
- Check Task Manager → CyberSafe should be running
- Look for `pythonw.exe` process
- GUI should appear within 2-3 seconds

**Q: Console still appears?**
- Make sure you're using `launcher.vbs` or updated `START.bat`
- Don't run `python main.py --gui` directly
- Use Desktop shortcut created by `CREATE_SHORTCUT.bat`

**Q: How to close the app?**
- Click the X button in GUI window
- Or right-click system tray icon (if available)

---

## ✅ **Verification**

After launch, you should see:
- ✅ CyberSafe GUI window
- ❌ NO black console/CMD window
- ✅ App in Task Manager as "pythonw.exe"

**Perfect! Professional GUI with no console clutter.** 🎉
