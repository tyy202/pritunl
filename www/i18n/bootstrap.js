define(['i18n'], function(i18n) {
  'use strict';

  // Make i18n available globally for templates
  window.i18n = i18n;

  // Patch _.templateSettings to include i18n in template scope
  var originalTemplate = _.template;
  _.template = function(text, settings) {
    var tpl_settings = settings || _.templateSettings;
    if (!tpl_settings.variable) {
      tpl_settings = _.extend({}, tpl_settings, {
        variable: 'data'
      });
    }
    var result = originalTemplate(text, tpl_settings);
    // Wrap the template function to inject i18n into scope
    var wrapped = function(data) {
      var i18n_data = _.extend({i18n: i18n}, data || {});
      return result(i18n_data);
    };
    return wrapped;
  };

  return i18n;
});
