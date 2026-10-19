/**
 * CyberSafe Network Monitor - Electron Main Process
 * Desktop application like Chrome/Claude
 */

const { app, BrowserWindow, Menu, Tray, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let tray;
let pythonProcess;
const API_URL = 'http://localhost:5000';

// Check if backend is running
async function checkBackend() {
  try {
    await axios.get(`${API_URL}/api/status`);
    return true;
  } catch (error) {
    return false;
  }
}

// Start Python backend
function startBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting Python backend...');
    
    // Get the path to the Python script
    const scriptPath = path.join(__dirname, '..', 'main.py');
    
    // Start Python process
    pythonProcess = spawn('python', [scriptPath, '--api'], {
      cwd: path.join(__dirname, '..'),
      detached: false
    });
    
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });
    
    pythonProcess.on('close', (code) => {
      console.log(`Backend exited with code ${code}`);
    });
    
    // Wait for backend to be ready
    let attempts = 0;
    const checkInterval = setInterval(async () => {
      attempts++;
      if (await checkBackend()) {
        clearInterval(checkInterval);
        resolve();
      } else if (attempts > 20) {
        clearInterval(checkInterval);
        reject(new Error('Backend failed to start'));
      }
    }, 500);
  });
}

// Stop Python backend
function stopBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    title: 'CyberSafe Network Monitor',
    backgroundColor: '#1a1a1a',
    show: false
  });
  
  // Load the app
  mainWindow.loadFile('index.html');
  
  // Show when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  
  // Handle window close
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Create menu
  createMenu();
}

// Create system tray
function createTray() {
  tray = new Tray(path.join(__dirname, 'assets', 'icon.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show CyberSafe',
      click: () => {
        mainWindow.show();
      }
    },
    {
      label: 'Start Monitoring',
      click: () => {
        mainWindow.webContents.send('start-monitoring');
      }
    },
    {
      label: 'Stop Monitoring',
      click: () => {
        mainWindow.webContents.send('stop-monitoring');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setContextMenu(contextMenu);
  tray.setToolTip('CyberSafe Network Monitor');
  
  tray.on('click', () => {
    mainWindow.show();
  });
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Start Monitoring',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('start-monitoring');
          }
        },
        {
          label: 'Stop Monitoring',
          accelerator: 'CmdOrCtrl+T',
          click: () => {
            mainWindow.webContents.send('stop-monitoring');
          }
        },
        { type: 'separator' },
        {
          label: 'Export Data',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            // TODO: Implement export
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://github.com/cybersafe-monitor');
          }
        },
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About CyberSafe',
              message: 'CyberSafe Network Monitor',
              detail: 'Version 1.0.0\n\nProfessional network traffic monitoring and threat detection.\n\n© 2026 CyberSafe'
            });
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App ready
app.whenReady().then(async () => {
  console.log('Starting CyberSafe Network Monitor...');
  
  try {
    // Check if backend is already running
    const backendRunning = await checkBackend();
    
    if (!backendRunning) {
      console.log('Backend not running, starting...');
      await startBackend();
    } else {
      console.log('Backend already running');
    }
    
    createWindow();
    createTray();
    
    console.log('Application ready!');
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox(
      'Startup Error',
      'Failed to start CyberSafe backend. Make sure Python and dependencies are installed.'
    );
    app.quit();
  }
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

// Cleanup on quit
app.on('before-quit', () => {
  app.isQuitting = true;
});

app.on('will-quit', () => {
  stopBackend();
});

// IPC handlers
ipcMain.handle('get-api-url', () => {
  return API_URL;
});

ipcMain.handle('check-backend', async () => {
  return await checkBackend();
});
