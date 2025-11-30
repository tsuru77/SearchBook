import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Build configuration for production
  build: {
    // Output directory
    outDir: 'dist',
    
    // Minify with esbuild (default, faster)
    minify: 'esbuild',
    
    // Source maps for production debugging
    sourcemap: true,
    
    // Chunk size warning threshold
    chunkSizeWarningLimit: 1000,
    
    // Optimize chunks
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },

  // Development server (used with npm run dev)
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },

  // Preview server (used with npm run preview)
  preview: {
    port: 4173,
  },
})
