const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  publicPath: '/static/vue/',
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000/service/api',
        changeOrigin: true,
      },
    },
  },
  outputDir: path.resolve(__dirname, '../backendApp/static/vue'),
})
