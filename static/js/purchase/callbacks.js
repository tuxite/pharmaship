/*jslint indent:4*/
/*globals formCallback, jQuery */

(function ($) {
    'use strict';

    /* Callback after modifying the name */
    document.formCallback.prototype.updateName = function (data) {
        // Update the name of the requisition
        $('#requisition-name').html(data.name);
        // Close the modal
        $('#action_modal').modal('hide');
    };

    /* Callback after modifying the status */
    document.formCallback.prototype.updateStatus = function (data) {
        // Update the status of the requisition
        $('#requisition-status').html(data.status);
        // Close the modal
        $('#action_modal').modal('hide');
    };

    /* Callback after a location change */
    document.formCallback.prototype.redirect = function (data) {
        window.location = data.url;
    };

    /* Callback after updating an item quantity in a requisition */
    document.formCallback.prototype.quantityFeedback = function (data) {
        if (data.success) {
            var button = $('#item-' + data.id + ' .qty-feedback');
            button.addClass('form-feedback');
            button.button('reset');
        }
    };
    /* Callback after adding an item in a requisition */
    document.formCallback.prototype.itemAdd = function (data) {
        if (data.success) {
            $('.ps-scroll-items').append(data.content); // NOTE: Use preprend to add first?
        }
    };
}(jQuery));
