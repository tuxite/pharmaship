/*jslint indent:4*/
/*globals formCallback, jQuery */

(function ($) {
    'use strict';

    /* Function to filter the objects by name */
    function filter_by_name() {
        // Issue #10:
        //  - added :visible selector to match only visible items.
        //  - fires the filter-tag event when no filter set..
        //  - move 'filter-tag' reset before firing filter-tag event
        //  Matthieu Morin 2014-11-07

        var input = $('#filter-input');

        $(input)
            .change(function () {
                var list = $(document).find('#item-list');
                // Reset the group filter
                $('#filter-select').val(0);
                $(list).find('div.group-div').show();
                // Reset the location filter
                $('#filter-location').val(0);

                var filter = $(this).val();
                if (filter) {
                    $(list).find("h4:visible:not(:contains(" + filter + "))").parents('.item-div').hide();
                    $(list).find("h4:visible:contains(" + filter + ")").parents('.item-div').show();
                } else {
                    // Show all the items, and apply tag filter if any
                    $(list).find("h4").parents('.item-div').show();
                    // Fire the filter-tag event
                    if ($('#filter-tag').hasClass("active") === true) {
                        // Reset the tag filter
                        $('#filter-tag').removeClass('active');
                        $('#filter-tag').click();
                    }
                }
                return false;
            })
            .keyup(function () {
                // fire the above change event after every letter
                $(this).change();
            });
    }

    /* Function to filter by group */
    function filter_by_group() {
        var input = $('#filter-group-select');

        $(input)
            .change(function () {
                var list = $(document).find('#item-list');
                // Reset the text filter
                $('#filter-input').val('');
                $(list).find(".group-div").show();

                var filter = $(this).val();
                if (filter !== 0) {
                    $(list).find("h3.group:not(:contains(" + filter + "))").parents('.group-div').hide();
                    $(list).find("h3.group:contains(" + filter + ")").parents('.group-div').show();
                }
                return false;
            });
    }

    /* Function to filter by tag */
    function filter_by_tag() {
        var input = $('#filter-tag'),
            filter = $(input).html();

        $(input).on('click', function (e) {
            var list = $(document).find('#item-list');
            if (!$(e.target).hasClass('active')) {
                $(list).find(".item-div").hide();
                $(list).find(".item-tag:contains(" + filter + ")").parents('.item-div').show();
            } else {
                $(list).find(".item-div").show();
            }
        });
    }

    /* Function to filter by location */
    function filter_by_location() {
        var input = $('#filter-location-select');

        $(input)
            .change(function () {
                var filter = $(this).val(),
                    list = $(document).find('#item-list');
                if (filter !== 0) {
                    $(list).find(".location:not(:contains(" + filter + "))").parents('.item-div').hide();
                    // Also hide empty objects (with no table)
                    $(list).find(":not(:has(.location))").parents('.item-div').hide();
                    $(list).find(".location:contains(" + filter + ")").parents('.item-div').show();
                } else {
                    $(list).find(".item-div").show();
                }
                return false;
            });
    }

    /* Function to filter by allowance */
    function filter_by_allowance() {
        var form = $('#filter-more'),
            allowance_checkbox = $("input.filter-check"),
            reset_checkbox = $("input[name=allowance-0]");

        $(reset_checkbox)
            .change(function () {
                // Reset the other filters
                $('#filter-reset').trigger("click");
                if (this.checked === true) {
                    // Uncheck the other checkboxes
                    $('.filter-check:checkbox:checked').prop('checked', false);
                    $(form).submit();
                }
            });

        $(allowance_checkbox)
            .change(function () {
                // Reset the other filters
                $('#filter-reset').trigger("click");
                // Uncheck of the reset checkbox
                $(reset_checkbox).prop('checked', false);
                // Check the reset checkbox if no allowance checkbox checked or all allowances checked.
                // Could be weird...
                if ($('.filter-check:checkbox:checked').length === 0 ||
                        $('.filter-check:checkbox:checked').length === $('.filter-check:checkbox').length
                        ) {
                    $(reset_checkbox).prop('checked', true);
                    $('.filter-check').prop('checked', false);
                }
                $(form).submit();
            });
    }

    /* Function to clear the text input when clicking on the button */
    function filter_reset() {
        var input = $('#filter-input'),
            group_select = $('#filter-group-select'),
            location_select = $('#filter-location-select'),
            tag_toggle = $('#filter-tag'),
            link = $('#filter-reset');

        $(link).click(function (e) {
            // Setting the values
            $(input).val('');
            $(group_select).val(0);
            $(location_select).val(0);
            $(tag_toggle).removeClass('active');
            // Calling the filter function
            var event = $.Event("change");
            $(input).trigger(event);
            // Prevents the default action to be triggered.
            e.preventDefault();
        });
    }

    /* DOM ready */
    $(function () {
        filter_reset();
        filter_by_name();
        filter_by_group();
        filter_by_tag();
        filter_by_location();
        filter_by_allowance();
    });
}(jQuery));
