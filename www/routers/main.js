define([
  'jquery',
  'underscore',
  'backbone',
  'models/authSession',
  'models/settings',
  'views/alert',
  'views/login',
  'views/dashboard',
  'views/admins',
  'views/users',
  'views/servers',
  'views/hosts',
  'views/links',
  'views/modalSettings'
], function($, _, Backbone, AuthSessionModel, SettingsModel, AlertView,
    LoginView, DashboardView, AdminsView, UsersView, ServersView, HostsView,
    LinksView, ModalSettingsView) {
  'use strict';
  var Router = Backbone.Router.extend({
    routes: {
      '': 'dashboard',
      'init': 'init',
      'dashboard': 'dashboard',
      'admins': 'admins',
      'users': 'users',
      'servers': 'servers',
      'hosts': 'hosts',
      'links': 'links',
      'logout': 'logout',
      'logout/:alert': 'logout'
    },
    initialize: function(data) {
      this.data = data;
      this.loadedStyles = {};
      this.currentLang = localStorage.getItem('pritunl_lang') || 'en';
    },
    updateTheme: function() {
      if (window.subActive && window.theme === 'dark') {
        $('body').addClass('dark');
      }
      else {
        $('body').removeClass('dark');
      }
    },
    onThemeLight: function() {
      window.theme = 'light';
      this.updateTheme();
    },
    onThemeDark: function() {
      window.theme = 'dark';
      this.updateTheme();
    },
    openSettings: function() {
      var model = new SettingsModel();
      model.fetch({
        success: function() {
          var modal = new ModalSettingsView({
            initial: true,
            model: model
          });
          this.listenToOnce(modal, 'applied', function() {
            var alertView = new AlertView({
              type: 'warning',
              message: 'Successfully saved settings.',
              dismissable: true
            });
            $('.alerts-container').append(alertView.render().el);
          }.bind(this));
        }.bind(this),
        error: function() {
          var alertView = new AlertView({
            type: 'danger',
            message: 'Failed to load authentication data, ' +
              'server error occurred.',
            dismissable: true
          });
          $('.alerts-container').append(alertView.render().el);
          this.addView(alertView);
        }.bind(this)
      });
    },
    auth: function(callback) {
      if (window.authenticated) {
        callback();
        return;
      }
      this.loginCallback = callback;
      if (this.loginView) {
        return;
      }
      $('.modal').modal('hide');
      this.loginView = new LoginView({
        alert: this.logoutAlert,
        callback: function() {
          this.loginView = null;
          window.authenticated = true;
          this.loginCallback();
          this.loginCallback = null;
        }.bind(this)
      });
      this.logoutAlert = null;
      if (this.loginView.active) {
        $('body').append(this.loginView.render().el);
      }
      else {
        this.loginView = null;
      }
    },
    loadStyles: function() {
    },
    loadPage: function(view) {
      this.loadStyles();
      var curView = this.data.view;
      this.data.view = view;
      $(this.data.element).fadeOut(100, function() {
        if (curView) {
          curView = curView.destroy();
        }
        $(this.data.element).html(this.data.view.render().el);
        $(this.data.element).fadeIn(300);
      }.bind(this));
    },
    init: function() {
      this.dashboard(true);
    },
    dashboard: function(init) {
      this.auth(function() {
        $('header .navbar .nav li').removeClass('active');
        $('header .dashboard').addClass('active');
        this.loadPage(new DashboardView());
        if (init) {
          this.openSettings();
          Backbone.history.navigate('dashboard');
        }
      }.bind(this));
    },
    admins: function() {
      this.auth(function() {
        $('header .navbar .nav li').removeClass('active');
        $('header .admins').addClass('active');
        this.loadPage(new AdminsView());
      }.bind(this));
    },
    users: function() {
      this.auth(function() {
        $('header .navbar .nav li').removeClass('active');
        $('header .users').addClass('active');
        this.loadPage(new UsersView());
      }.bind(this));
    },
    servers: function() {
      this.auth(function() {
        $('header .navbar .nav li').removeClass('active');
        $('header .servers').addClass('active');
        this.loadPage(new ServersView());
      }.bind(this));
    },
    hosts: function() {
      this.auth(function() {
        $('header .navbar .nav li').removeClass('active');
        $('header .hosts').addClass('active');
        this.loadPage(new HostsView());
      }.bind(this));
    },
    links: function() {
      this.auth(function() {
        $('header .navbar .nav li').removeClass('active');
        $('header .links').addClass('active');
        this.loadPage(new LinksView());
      }.bind(this));
    },
    logout: function(alert) {
      if (alert === 'expired') {
        this.logoutAlert = 'Session has expired, please log in again';
      }
      var authSessionModel = new AuthSessionModel({
        id: true
      });
      authSessionModel.destroy({
        success: function() {
          window.authenticated = false;
          window.location = '';
        }.bind(this),
        error: function() {
          var alertView = new AlertView({
            type: 'danger',
            message: 'Failed to logout, server error occurred.',
            dismissable: true
          });
          $('.alerts-container').append(alertView.render().el);
          if (this.data.view) {
            this.data.view.addView(alertView);
          }
        }.bind(this)
      });
    }
  });

  var initialize = function() {
    var _ajax = Backbone.ajax;
    Backbone.ajax = function(options) {
      options.complete = function(response) {
        if (response.status === 401) {
          window.authenticated = false;
          Backbone.history.navigate('logout/expired', {trigger: true});
        }
      };
      return _ajax.call(Backbone.$, options);
    };

    var data = {
      element: '#app',
      view: null
    };

    var router = new Router(data);
    Backbone.history.start();
    return router;
  };

  return {
    initialize: initialize
  };
});
