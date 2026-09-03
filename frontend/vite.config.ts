import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// O `/api` é servido pelo backend, não pelo Vite.
//
// Passar por proxy no desenvolvimento evita CORS por completo: para o navegador, tudo
// vem da mesma origem. É por isso que o backend continua sem CORS (BACKLOG §B14.3) —
// a decisão de qual origem liberar pertence ao lugar onde o app for hospedado, e
// inventá-la agora seria decidir cedo demais.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.BACKEND ?? 'http://localhost:8787',
        changeOrigin: true,
        rewrite: (caminho) => caminho.replace(/^\/api/, ''),
      },
    },
  },
})
