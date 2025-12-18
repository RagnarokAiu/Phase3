import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/users': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/users/, '')
      },
      '/api/chat': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/chat/, '')
      },
      '/api/documents': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/documents/, '')
      },
      '/api/quiz': {
        target: 'http://127.0.0.1:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/quiz/, '')
      },
      '/api/stt': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/stt/, '')
      },
      '/api/tts': {
        target: 'http://127.0.0.1:8006',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/tts/, '')
      }
    }
  }
})
