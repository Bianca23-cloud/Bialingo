'use strict';
/* Bialingo pour Windows et Linux : une fenêtre qui affiche l'application, entièrement hors ligne.
   Aucune page distante n'est chargée ; les liens externes s'ouvrent dans le navigateur. */
const { app, BrowserWindow, session, shell } = require('electron');
const path = require('path');

if (!app.requestSingleInstanceLock()) app.quit();

function createWindow() {
  const win = new BrowserWindow({
    width: 1100, height: 820, minWidth: 360, minHeight: 560,
    title: 'Bialingo', backgroundColor: '#FBF7FF', autoHideMenuBar: true,
    icon: path.join(__dirname, 'app', 'icon.png'),
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false, spellcheck: false }
  });
  win.loadFile(path.join(__dirname, 'app', 'index.html'));
  // Liens externes (code source, mentions) : navigateur par défaut ; jamais de navigation hors de l'application.
  win.webContents.setWindowOpenHandler(({ url }) => { if (url.startsWith('https://')) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (!url.startsWith('file://')) { e.preventDefault(); if (url.startsWith('https://')) shell.openExternal(url); } });
}

app.whenReady().then(() => {
  // Seule autorisation accordée : le micro, pour les exercices de prononciation (enregistrement local).
  session.defaultSession.setPermissionRequestHandler((wc, permission, callback) => callback(permission === 'media'));
  createWindow();
});
app.on('second-instance', () => { const w = BrowserWindow.getAllWindows()[0]; if (w) { if (w.isMinimized()) w.restore(); w.focus(); } });
app.on('window-all-closed', () => app.quit());
