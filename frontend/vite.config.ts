import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import { resolve } from 'node:path';
import { createPinia } from 'pinia';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      vue({
        template: {
          compilerOptions: {
            isCustomElement: (tag) => tag.startsWith('swiper-')
          }
        }
      }),
      createPinia()
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 3000,
      host: '0.0.0.0',
      strictPort: true,
      open: 'http://default.shopacoffee.local:3000',
      allowedHosts: ['default.shopacoffee.local', '*.shopacoffee.local'],
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      },
      fs: {
        strict: true,
      },
    },
    build: {
      target: 'esnext',
      minify: 'esbuild',
      sourcemap: true,
      outDir: 'dist',
      assetsDir: 'assets',
      rollupOptions: {
        input: {
          main: fileURLToPath(new URL('./index.html', import.meta.url))
        },
        output: {
          manualChunks: {
            'vue': ['vue', 'vue-router', 'pinia'],
            'vendor': ['axios', '@headlessui/vue', '@heroicons/vue']
          }
        }
      },
      commonjsOptions: {
        esmExternals: true
      }
    },
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV || 'development'),
      'process.env': {}
    },
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'axios',
        '@headlessui/vue',
        '@heroicons/vue/outline',
        '@heroicons/vue/solid'
      ],
      exclude: ['@tailwindcss/forms']
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
      include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
      deps: {
        inline: ['@vue', '@vue/test-utils']
      }
    }
  };
});
