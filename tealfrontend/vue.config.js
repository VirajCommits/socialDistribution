const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  publicPath: '/',
  transpileDependencies: true,
  outputDir: path.resolve(__dirname, '../backendApp/static/vue'),
})
