const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  publicPath: '/static/vue/',
  transpileDependencies: true,
  outputDir: path.resolve(__dirname, '../backendApp/static/vue'),
})
