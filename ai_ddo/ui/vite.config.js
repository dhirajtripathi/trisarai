import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5179,
        proxy: {
            '/po': 'http://127.0.0.1:8006',
            '/sm': 'http://127.0.0.1:8006',
            '/config': 'http://127.0.0.1:8006',
            '/pma': 'http://127.0.0.1:8006',
            '/projma': 'http://127.0.0.1:8006',
            '/pgma': 'http://127.0.0.1:8006',
            '/orch': 'http://127.0.0.1:8006'
        }
    }
})
