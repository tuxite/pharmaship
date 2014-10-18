/*globals jQuery */
/*jslint devel: true*/

(function ($) {
    "use strict";

    /* Function to delete an item when clicking on the delete button */
    function delete_item() {
        $(document).on('click', '.btn-delete', function (e) {
            e.preventDefault();

            var button = $(e.target),
                item = button.parents('tr:first');

            console.log(e, item);
            // Set the loading state
            button.button('loading');
            // call the link
            $.ajax({
                url: e.target.href,
                success: function (data) {
                    // Reset the button
                    button.button('reset');
                    // Delete the content
                    item.remove();
                }
            });
        });
    }

    /* Function to delete an item when clicking on the delete button */
    function toggle_item() {
        $(document).on('click', '.btn-toggle', function (e) {
            e.preventDefault();
            // Reset
            $('.form-feedback').remove();

            var button = $(e.target).closest('a'),
                item = button.parents('tr:first');

            // Set the loading state
            button.button('loading');
            // call the link
            $.ajax({
                url: $(button).attr('href'),
                success: function (data) {
                    // Reset the button
                    button.button('reset');
                    // Update the row
                    item.replaceWith(data.content);
                },
                error: function (data) {
                    console.log(data.responseText);
                    // Process the error message
                    var errors = JSON.parse(data.responseText);
                    // Reset the button
                    button.button('reset');
                    // Return an error message
                    button.parent().append("<span class='text-danger form-feedback'><b>" + errors.error + "</b></span>");
                }
            });
        });
    }

    /* DOM ready */
    $(function () {
        /* Loading functions */
        delete_item();
        toggle_item();
    });

}(jQuery));
