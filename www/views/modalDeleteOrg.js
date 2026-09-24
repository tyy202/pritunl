define([
  'jquery',
  'underscore',
  'backbone',
  'views/modal',
  'views/alert',
  'text!templates/modalDeleteOrg.html'
], function($, _, Backbone, ModalView, AlertView, modalDeleteOrgTemplate) {
  'use strict';
  var ModalDeleteOrgView = ModalView.extend({
    className: 'delete-org-modal',
    template: _.template(modalDeleteOrgTemplate),
    title: i18n.t('modal.modalDeleteOrg.title'),
    okText: 'Delete',
    inputMatch: true,
    initialize: function() {
      ModalDeleteOrgView.__super__.initialize.call(this);
      var alertView = new AlertView({
        type: 'danger',
        message: i18n.t('msg.deleteOrgConfirm').substring(0, i18n.t('msg.deleteOrgConfirm').length - 1) + ' ' +
          'in it. Any servers that are attached to the organization will ' +
          'be stopped.',
        animate: false
      });
      this.addView(alertView);
      this.$('.modal-body').prepend(alertView.render().el);
      this.inputMatchText = this.model.get('name');
    },
    body: function() {
      return this.template();
    },
    onOk: function() {
      this.setLoading('Deleting organization...');
      this.model.destroy({
        success: function() {
          this.close(true);
        }.bind(this),
        error: function(model, response) {
          this.clearLoading();
          if (response.responseJSON) {
            this.setAlert('danger', response.responseJSON.error_msg);
          }
          else {
            this.setAlert('danger', this.errorMsg);
          }
        }.bind(this)
      });
    }
  });

  return ModalDeleteOrgView;
});
