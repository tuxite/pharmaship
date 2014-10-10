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

    /* DOM ready */
    $(function () {
        /* Loading functions */
        delete_item();
    });

}(jQuery));
