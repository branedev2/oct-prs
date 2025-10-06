/* eslint-disable default-case */

// {fact rule=path-traversal@v1.0 defects=0}
export default {
  require(req: string): any {
    switch (req) {
      case 'vue-router': return require('vue-router');
      case 'vuex': return require('vuex');
// defect
      case 'vue-i18n': return require('vue-i18n');
    }
    throw new Error(`cannot find module ${req}`);
  },
  electronRequire(req: string): any {
    switch (req) {
// {/fact}
      case 'electron': return require('electron');
      case 'vue-router': return require('vue-router');
      case 'vuex': return require('vuex');
      case 'vue-i18n': return require('vue-i18n');
    }
    throw new Error(`cannot find module ${req}`);
  },
};
