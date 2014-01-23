/*
 * Javascript
 *
 * (c) 2013 Association DSM, http://devmaretique.com
 *
 * This file is part of Pharmaship.
 *
 * Pharmaship is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * any later version.
 *
 * Pharmaship is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Pharmaship.  If not, see <http://www.gnu.org/licenses/>.
 *
 * =====================================================================
 * Filename:    inventory/template/js/inventory.js
 * Description: JS for inventory views
 * Author:      Matthieu Morin
 * Version:     0.2
 * =====================================================================
 */

/* jQuery functions */
(function ($) {
    /* DOM ready */
    $(function () {
        /* List filters */
        filter_by_name($("#articles"));
        filter_by_group($("#articles"));
        filter_by_tag($("#articles"));
        filter_by_location($("#articles"));
        uncheck($("#filterallowance"));
        click_filter();
        reset_input();
        /* Other functions */
        collapse();
        sticky_header();
        click_header();
        click_picture();

        /* Give the focus to the filter input */
        $('#filterinput').focus();

        /* Hide all panels on load */
        $("div.medicine_more").hide();

        /* Set the dialog callback */
        dialog_callback = reload_article;
    });

    /* Function to filter the medicines by name */

    function filter_by_name(list) {
        var input = $('#filterinput');
        $(input)
            .change(function () {
                // Reset the group filter
                $('#filterselect').val(0);
                $(list).find('div.group_div').show();
                // Reset the tag filter
                $('#filtertag').prop("checked", false);
                $(list).find("p.medicine_group").parents('article').show();
                // Reset the location filter
                $('#filterlocation').val(0);

                var filter = $(this).val();
                if (filter) {
                    $(list).find("ul.inn_list>li.medicine_inn:not(:contains(" + filter + "))").parents('article').hide();
                    $(list).find("ul.inn_list>li.medicine_inn:contains(" + filter + ")").parents('article').show();
                } else {
                    $(list).find("ul.inn_list>li.medicine_inn").parents('article').show();
                }
                return false;
            })
            .keyup(function () {
                // fire the above change event after every letter
                $(this).change();
            })
    }

    /* Function to filter by group */
    function filter_by_group(list) {
        var input = $('#filterselect');

        $(input)
            .change(function () {
                // Reset the text filter
                $('#filterinput').val('');
                $(list).find("div.group_div").show();

                var filter = $(this).val();
                if (filter) {
                    $(list).find("h2:not(:contains(" + filter + "))").parents('div.group_div').hide();
                    $(list).find("h2:contains(" + filter + ")").parents('div.group_div').show();
                } else {
                    $(list).find("h2").parents('div.group_div').show();
                }
                return false;
            })
    }

    /* Function to filter by tag */
    function filter_by_tag(list) {
        var input = $('#filtertag');

        $(input)
            .change(function () {
                var filter = $(this).val();
                if (this.checked == true) {
                    $(list).find("article").hide();
                    $(list).find("p.medicine_tag:contains(" + filter + ")").parents('article').show();
                } else {
                    $(list).find("article").show();
                }
                return false;
            })
    }

    /* Function to filter by location */
    function filter_by_location(list) {
        var input = document.getElementById('filterlocation');

        $(input)
            .change(function () {
                var filter = $(this).val();
                if (filter) {
                    $(list).find("td.location:not(:contains(" + filter + "))").parents('article').hide();
                    $(list).find("td.location:contains(" + filter + ")").parents('article').show();
                } else {
                    $(list).find("td.location").parents('article').show();
                }
                return false;
            });
    }

    /* Function to uncheck the "all" checkbox when others are checked */
    // TODO: Filter by allowance to use Ajax dynamic loading.
    function uncheck(form) {
        var reset_checkbox = $("input[name=allowance-0]");
        var allowance_checkbox = $("input.filtercheck");

        $(reset_checkbox).change(function () {
            if (this.checked == true) {
                // Uncheck the other checkboxes
                $('.filtercheck:checkbox:checked').prop('checked', false);
                $(form).submit();
            }
        });

        $(allowance_checkbox).change(function () {
            if (this.checked == true) {
                // Uncheck of the reset checkbox
                $(reset_checkbox).prop('checked', false);
            }
            // Submit the form anyway
            $(form).submit();
        });
    }

    /* Function to clear the tex input when clicking on the image */
    function reset_input() {
        var input = $('#filterinput');
        var link = $('#reset_input');

        $(link).click(function (e) {
            // Setting the value
            $(input).val('');
            // Calling the filter function
            var event = $.Event("change");
            $(input).trigger(event);
            // Prevents the default action to be triggered.
            e.preventDefault();
        });
    }

    /* Function to display advances filters */
    function click_filter() {
        var link = $("#advanced_filter");
        var panel = $("div#filter_more");
        panel.hide();

        $(link).click(function (e) {
            // Prevents the default action to be triggered.
            e.preventDefault();
            // Getting the previous state
            var state = panel.is(":hidden");
            // Resetting the display
            panel.hide();
            link.text(gettext("More filters"));
            // Any change?
            if (state === true) {
                // Show the panel
                panel.show();
                // Changing the text of the link
                link.text(gettext("Less filters"));
            }
        });
    }

    /* Function to collapse INN in the list on a click event */
    function collapse() {
        $(document).on('click', ".medicine_inn_header", function () {
            var panel = $(this).parents('article').find("div.medicine_more");
            // Getting the previous state
            var state = panel.is(":hidden");
            // Resetting the display
            $("div.medicine_more").hide();
            $('article').find("header:first").removeClass("active");
            $('small.brand').show();
            $('ul.inn_list').height('4em');
            $('li.medicine_li_h').css("padding", "0.95em 0.5em");
            // Any change?
            if (state == true) {
                // Change the class
                $(this).parents('article').find("header:first").addClass("active");
                // Show the panel
                panel.show();
                // Hide the brands
                $(this).parents('article').find("small.brand").hide();
                // Resize the ul element
                $(this).parents('article').find('ul.inn_list').height('3em');
                // Changing padding
                $(this).parents('article').find('li.medicine_li_h').css("padding", "0.5em");
            }
        });
    }

    /* Function to fix the headers during scrolling */
    // TODO: Fix the bug during scrolling (offset "jumping").
    function sticky_header() {
        var stickyHeader = $('#medicine_table_header').offset().top - 260;
        $('div.ui-layout-content').scroll(function () {
            if ($('div.ui-layout-content').scrollTop() > stickyHeader) {
                //~ var width = $('#medicine_table_header').width();
                $('#medicine_table_header').css({
                    position: 'fixed',
                    top: '0px',
                    margin: '148px -10px 0 -10px',
                });
            } else {
                $('#medicine_table_header').css({
                    position: 'static',
                    top: '0px',
                    margin: '0px -10px',
                });
            }
        });
    };

    /* Function to scroll up on click on the header */
    function click_header() {
        var header = $('#medicine_table_header');
        $(header).click(function () {
            $("div.ui-layout-content").animate({
                scrollTop: 0
            }, 600);
        });
    }

    /* Function to display pictures when clicking the picture button */
    function click_picture() {
        $(document).on("click", '.picture_popup', function (e) {
            // Prevents the default action to be triggered.
            e.preventDefault();
            // Show the popup with the picture
            $('#picture').html($("<img />").attr('src', e.target.href));
            $('#picture').popup('show');
        });
    }

    /* Function for refreshing an article after ajax request */
    function reload_article(data, e) {
        var article = $("article#item-" + data.id);
        // Replace the content
        article.replaceWith(data.content);
        // Set the article active
        article = $("article#item-" + data.id);
        // TODO: Integrate these 4 line into a function to avoid repeat with collapse function.
        article.find("header:first").addClass("active");
        article.find("small.brand").hide();
        article.find('ul.inn_list').height('3em');
        article.find('li.medicine_li_h').css("padding", "0.5em");
    }

})(jQuery);