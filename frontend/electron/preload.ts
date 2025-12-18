import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
  platform: process.platform,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron,
  },
  print: {
    getPrinters: () => ipcRenderer.invoke('print:get-printers'),
    printHTML: (html: string, options?: any) => ipcRenderer.invoke('print:html', html, options),
    printSilent: (html: string, printerName?: string, paperWidth?: number) => 
      ipcRenderer.invoke('print:silent', html, printerName, paperWidth),
  },
});
