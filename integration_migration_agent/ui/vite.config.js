import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5178,
    proxy: {
      '/cases': 'http://127.0.0.1:8005',
      '/prompts': 'http://127.0.0.1:8005',
      '/kb': 'http://127.0.0.1:8005',
    }
  }
})
