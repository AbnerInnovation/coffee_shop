export interface PrinterInfo {
  name: string;
  displayName: string;
  description: string;
  status: number;
  isDefault: boolean;
  options?: Record<string, any>;
}

export interface PrintResult {
  success: boolean;
  error?: string;
  printer?: string;
}

export interface ElectronAPI {
  platform: string;
  versions: {
    node: string;
    chrome: string;
    electron: string;
  };
  print: {
    getPrinters: () => Promise<PrinterInfo[]>;
    printHTML: (html: string, options?: any) => Promise<PrintResult>;
    printSilent: (html: string, printerName?: string, paperWidth?: number) => Promise<PrintResult>;
  };
}

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}
