define([
  'jquery',
  'underscore',
  'backbone',
  'models/settings',
  'models/user',
  'collections/userAudit',
  'views/alert',
  'views/modalLogs',
  'views/modalSettings',
  'text!templates/header.html'
], function($, _, Backbone, SettingsModel, UserModel,
    UserAuditCollection, AlertView, ModalLogsView, ModalSettingsView,
    headerTemplate) {
  'use strict';
  var HeaderView = Backbone.View.extend({
    tagName: 'header',
    template: _.template(headerTemplate),
    events: {
      'click .logs a': 'openLogs',
      'click .change-password a': 'openSettings',
      'click .lang-switch': 'switchLanguage'
    },
    initialize: function() {
      this.model = new SettingsModel();
      this.listenTo(window.events, 'settings_updated', this.update);
      this.currentLang = localStorage.getItem('pritunl_lang') || 'en';
      this.update();
      HeaderView.__super__.initialize.call(this);
    },
    render: function() {
      this.$el.html(this.template());
      this.updateLangLabel();
      return this;
    },
    updateLangLabel: function() {
      this.$('.lang-switch').text(this.currentLang === 'zh' ? 'EN' : '中文');
    },
    switchLanguage: function() {
      var newLang = this.currentLang === 'en' ? 'zh' : 'en';
      localStorage.setItem('pritunl_lang', newLang);
      this.currentLang = newLang;
      window.location.reload();
    },
    update: function() {
      this.model.fetch({
        success: function(model) {
          if (model.get('auditing') === 'all') {
            this.$('.audit-admin a').css('display', 'block');
          }
          else {
            this.$('.audit-admin a').hide();
          }
        }.bind(this),
        error: function() {
          var alertView = new AlertView({
            type: 'danger',
            message: i18n.t('msg.failedLoadSettings').substring(0, i18n.t('msg.failedLoadSettings').length - 1) + ' ' +
              'server error occurred.',
            dismissable: true
          });
          $('.alerts-container').append(alertView.render().el);
          this.addView(alertView);
        }.bind(this)
      });
    },
    openLogs: function() {
      var modal = new ModalLogsView();
      this.addView(modal);
    },
    openSettings: function() {
      var model = new SettingsModel();
      model.fetch({
        success: function() {
          var modal = new ModalSettingsView({
            model: model
          });
          this.listenToOnce(modal, 'applied', function() {
            var alertView = new AlertView({
              type: 'success',
              message: i18n.t('msg.successSaveSettings'),
              dismissable: true
            });
            $('.alerts-container').append(alertView.render().el);
          }.bind(this));
        }.bind(this),
        error: function() {
          var alertView = new AlertView({
            type: 'danger',
            message: i18n.t('msg.failedLoadSettings').substring(0, i18n.t('msg.failedLoadSettings').length - 1) + ' ' +
              'server error occurred.',
            dismissable: true
          });
          $('.alerts-container').append(alertView.render().el);
          this.addView(alertView);
        }.bind(this)
      });
    }
  });

  return HeaderView;
});
