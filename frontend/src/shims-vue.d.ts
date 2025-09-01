/* eslint-disable */
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare module '*.json' {
  const value: any;
  export default value;
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.bmp' {
  const content: string;
  export default content;
}

declare module '*.tiff' {
  const content: string;
  export default content;
}

// For environment variables
declare interface ImportMetaEnv {
  VITE_API_URL: string;
  // Add other environment variables here
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Global type declarations
declare module 'pinia' {
  export interface PiniaCustomProperties {
    // Add any custom properties/methods you add to the store
  }
}

// Extend the Window interface if you add any global properties to window
interface Window {
  // Add any global properties you add to window
}
