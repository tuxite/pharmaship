/*globals jQuery */
/*jslint devel: true*/

(function ($) {
    "use strict";

    /* Function to handle autocomplete when adding and item to a requisistion */
    function set_autocomplete() {
        var search_url = $("input[name=name_search_url]").val();

    }

    /* Function to send the new item form */
    function add_item() {
        $(document).on('click', '.item_submit', function (e) {
            e.preventDefault();
            var form = $("form[name=new_item]");
            // Set the object_id in the form
            $(form).find("input[name=object_id]").val($("input[name=new_item_name]").select2("val"));
            // Submit the form
            form.submit();
        });
    }

    /* Function to modify the quantity on focus change */
    function update_quantity() {
        $(document).on('focusout', '.update-on-focus', function (e) {
            // Get the id of the item
            var item = $(e.target).attr('name').split('item_qty-')[1],
                quantity = $(e.target).val(),
                form = $('#update-form'),
                button = $('<button class="btn btn-link qty-feedback" data-loading-text="<span class=\'fa fa-spinner fa-spin\'></span>"><span class="fa fa-check text-success"></span></button>');
            // Set the values for the form
            $('input[name=item_id]').val(item);
            $('input[name=item_qty]').val(quantity);
            // Add a 'loading' button
            item = $(e.target).parents("div.row:first").find(".actions");
            button.appendTo(item);
            button.button('loading');
            // Send the form
            form.submit();
        });
    }

    /* Function to delete an item when clicking on the delete button */
    function delete_item() {
        $(document).on('click', '.btn-delete', function (e) {
            e.preventDefault();
            // Reset
            $('.form-feedback').remove();

            var button = $(e.target).closest('a'),
                item = button.parents('.row:first');

            // Set the loading state
            button.button('loading');
            // call the link
            $.ajax({
                url: $(button).attr('href'),
                success: function (data) {
                    // Reset the button
                    button.button('reset');
                    // Delete the content
                    item.remove();
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
        set_autocomplete();
        add_item();
        delete_item();
        update_quantity();

        $('.select2, .select2-multiple').select2({
            minimumInputLength: 2,
            ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
                url: $('input[name=name_search_url]').val(),
                dataType: 'json',
                type: 'post',
                data: function (term, page) {
                    return {
                        name: term // search term
                    };
                },
                results: function (data, page) { // parse the results into the format expected by Select2.
                    return {
                        results: data
                    };
                }
            }
        });
    });
}(jQuery));
