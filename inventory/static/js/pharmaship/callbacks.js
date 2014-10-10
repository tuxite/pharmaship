/*jslint indent:4*/
/*globals formCallback, jQuery */

(function ($) {
    'use strict';
    /* Callback after modification of an article */
    document.formCallback.prototype.updateArticle = function (data) {
        // Update the content
        $('#item-' + data.id).replaceWith(data.content);
        // Close the modal
        $('#action_modal').modal('hide');
    };
    /* Callback after modification of a remark */
    document.formCallback.prototype.updateRemark = function (data) {
        // Update the content
        $('#remark-' + data.id).html(data.content);
        // Close the modal
        $('#action_modal').modal('hide');
    };

    /* Callback after selecting the allowances */
    document.formCallback.prototype.updateList = function (data) {
        // Update the content
        $('#item-list').replaceWith(data);
    };

    /* Callback after adding a Location. */
    document.formCallback.prototype.addLocation = function (data) {
        var table = $(".location-table > tbody");
        table.append(data.location);

        // Close the modal
        $("#location_add_modal").modal('hide');
        // Clean the modal fields
        $(".modal-body input").val('');
        $('.form-feedback').remove();
    };
})(jQuery);
