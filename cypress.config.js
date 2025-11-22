const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    setupNodeEvents(on, config) {
      return config
    },
    
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    pageLoadTimeout: 30000,
    
    retries: {
      runMode: 2,
      openMode: 0
    },
    
    // Espera entre specs
    experimentalInteractiveRunEvents: true
  }
})