/**
 * Preload script - Bridge between main and renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getApiUrl: () => ipcRenderer.invoke('get-api-url'),
  checkBackend: () => ipcRenderer.invoke('check-backend'),
  onStartMonitoring: (callback) => ipcRenderer.on('start-monitoring', callback),
  onStopMonitoring: (callback) => ipcRenderer.on('stop-monitoring', callback)
});
