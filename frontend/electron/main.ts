import { app, BrowserWindow, shell, ipcMain, WebContents } from 'electron';
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

// IPC Handlers for printing
ipcMain.handle('print:get-printers', async () => {
  try {
    if (!win || !win.webContents) {
      console.error('❌ Main window not available');
      return [];
    }
    
    // Use getPrintersAsync for modern Electron versions
    let printers = [];
    
    if (typeof win.webContents.getPrintersAsync === 'function') {
      printers = await win.webContents.getPrintersAsync();
    } else if (typeof win.webContents.getPrinters === 'function') {
      printers = win.webContents.getPrinters();
    } else {
      return [];
    }
    
    
    return printers;
  } catch (error) {
    return [];
  }
});

ipcMain.handle('print:html', async (event, html: string, options?: any) => {
  try {
    if (!win) throw new Error('No window available');
    
    // Create a hidden window for printing
    const printWindow = new BrowserWindow({
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
      },
    });

    await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    
    // Wait for content to load
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Show print dialog
    const result = await printWindow.webContents.print(options || {});
    
    printWindow.close();
    return { success: result };
  } catch (error: any) {
    console.error('❌ Error printing:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('print:silent', async (event, html: string, printerName?: string, paperWidth: number = 80) => {
  return new Promise((resolve) => {
    try {
      // Create a hidden window for printing
      const printWindow = new BrowserWindow({
        show: false,
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true,
        },
      });

      printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
      
      printWindow.webContents.on('did-finish-load', async () => {
        try {
          // Get available printers using async method if available
          let printers = [];
          if (typeof printWindow.webContents.getPrintersAsync === 'function') {
            printers = await printWindow.webContents.getPrintersAsync();
          } else if (typeof printWindow.webContents.getPrinters === 'function') {
            printers = printWindow.webContents.getPrinters();
          }
          
          // Find the specified printer or use default
          let targetPrinter = printerName;
          if (!targetPrinter && printers.length > 0) {
            const defaultPrinter = printers.find(p => p.isDefault);
            targetPrinter = defaultPrinter?.name;
          }
          
          // Configure print options for thermal printer
          const printOptions: any = {
            silent: true,
            printBackground: true,
            margins: {
              marginType: 'none'
            },
            pageSize: {
              width: paperWidth * 1000, // Convert mm to microns
              height: 297000 // Auto height
            }
          };
          
          
          // Print silently
          printWindow.webContents.print(printOptions, (success, failureReason) => {
            printWindow.close();
            resolve({ success, printer: targetPrinter, error: failureReason });
          });
        } catch (error: any) {
          printWindow.close();
          resolve({ success: false, error: error.message });
        }
      });
      
      // Handle load errors
      printWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        console.error('❌ Failed to load print content:', errorDescription);
        printWindow.close();
        resolve({ success: false, error: errorDescription });
      });
    } catch (error: any) {
      console.error('❌ Error in silent print:', error);
      resolve({ success: false, error: error.message });
    }
  });
});

app.whenReady().then(createWindow);
