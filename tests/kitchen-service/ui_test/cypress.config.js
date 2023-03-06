const { defineConfig } = require("cypress");
const dotenv = require('dotenv');

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      dotenv.config({ path: `../../../.${process.env.ENV}.env` });
      config.env = {
        ...config.env,
        ...process.env
      }
      console.log('Config', config.env)
      return config
    },
  },
});
