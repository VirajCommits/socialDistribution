const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  publicPath: '/static/vue/',
  transpileDependencies: true,
  productionSourceMap: false,
  filenameHashing: true,
  devServer: {
    proxy: {
      '/service/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  outputDir: path.resolve(__dirname, '../backendApp/static/vue')
})