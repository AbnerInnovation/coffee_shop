import { app, BrowserWindow, shell } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Set up paths for packaged app
const RESOURCES_PATH = app.isPackaged
  ? path.join(process.resourcesPath, 'app.asar')
  : __dirname;

process.env.DIST = app.isPackaged
  ? path.join(RESOURCES_PATH, 'dist')
  : path.join(__dirname, '../dist');

process.env.VITE_PUBLIC = app.isPackaged
  ? path.join(RESOURCES_PATH, 'dist')
  : path.join(__dirname, '../public');

let win: BrowserWindow | null;
const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL'];

function createWindow() {
  win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(process.env.VITE_PUBLIC, 'favicon.png'),
    webPreferences: {
      preload: app.isPackaged
        ? path.join(RESOURCES_PATH, 'dist-electron', 'preload.js')
        : path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
    },
    autoHideMenuBar: true,
    backgroundColor: '#1f2937',
  });

  // Open external links in browser
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  // Enable DevTools in development
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL);
    win.webContents.openDevTools();
  } else {
    // Load from packaged files using file:// protocol
    const distPath = process.env.DIST ?? path.join(__dirname, '../dist');
    const indexPath = app.isPackaged
      ? path.join(RESOURCES_PATH, 'dist', 'index.html')
      : path.join(distPath, 'index.html');
    
    // Use loadURL with file:// protocol instead of loadFile
    // This ensures proper base URL for Vue Router
    win.loadURL(`file://${indexPath.replace(/\\/g, '/')}`);
    
    // DevTools disabled in production
    // Uncomment for debugging: win.webContents.openDevTools();
  }
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
    win = null;
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.whenReady().then(createWindow);
