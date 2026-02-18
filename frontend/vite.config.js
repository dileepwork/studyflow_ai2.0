import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        timeout: 60000,
        proxyTimeout: 60000,
      }
    }
  },
  build: {
    // Code-splitting optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // Split React and React-DOM into separate chunk
          'react-vendor': ['react', 'react-dom'],
          // Split charts library (usually large)
          'charts': ['recharts'],
          // Split animation library
          'motion': ['framer-motion'],
          // Split other UI libraries
          'ui-libs': ['lucide-react', 'react-dropzone', 'clsx', 'tailwind-merge'],
          // Split axios separately
          'http': ['axios']
        }
      }
    },
    // Enable CSS code splitting
    cssCodeSplit: true,
    // Optimize chunk size
    chunkSizeWarningLimit: 600
  }
})
