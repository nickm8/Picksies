// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  css: {
    postcss: './postcss.config.js',
  },
  build: {
    manifest: true,
    outDir: 'static/dist',
    rollupOptions: {
      input: 'resources/js/app.js'
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    hmr: {
      host: 'localhost'
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'resources/js'),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  }
})
