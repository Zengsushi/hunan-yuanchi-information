const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    client: {
      overlay: {
        errors: true,
        warnings: false,
        runtimeErrors: (error) => {
          const ignoreErrors = [
            "ResizeObserver loop completed with undelivered notifications",
            "ResizeObserver loop limit exceeded",
            "Non-passive event listener",
            "Script error"
          ];
          if (ignoreErrors.some(errorMessage => error.message.includes(errorMessage))) {
            return false;
          }
          return true;
        }
      }
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      },
      '/websocket': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          '^/websocket': '/ws'
        }
      }
    }
  }
})
