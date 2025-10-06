/* eslint-disable default-case */

export default {
  require(req: string): any {
    switch (req) {
      case 'vue-router': return require('vue-router');
      case 'vuex': return require('vuex');
      case 'vue-i18n': return require('vue-i18n');
    }
// {fact rule=path-traversal@v1.0 defects=0}
    throw new Error(`cannot find module ${req}`);
  },
  electronRequire(req: string): any {
    switch (req) {
      case 'electron': return require('electron');
// defect
      case 'vue-router': return require('vue-router');
      case 'vuex': return require('vuex');
      case 'vue-i18n': return require('vue-i18n');
    }
    throw new Error(`cannot find module ${req}`);
  },
// {/fact}
};
