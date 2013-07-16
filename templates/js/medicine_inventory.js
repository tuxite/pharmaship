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
 * Filename:    template/js/medicine_inventory.js
 * Description: JS for medicine inventory view
 * Author:      Matthieu Morin
 * Version:     0.1
 * =====================================================================
 */

/* jQuery functions */
;
(function ($) {

    /* DOM ready */
    $(function () {
        /* List filters */
        medicineFilter_by_name($("#articles"));
        medicineFilter_by_group($("#articles"));
        medicineFilter_by_tag($("#articles"));
        medicineFilter_by_location($("#articles"));
        uncheck($("#filterallowance"));
        collapse();
        sticky_header();
        click_header();
        reset_input();

        /* Hide all panels on load */
        $("div.medicine_more").hide();

        /* jQuery wrapper for handling clicks to open popups */
        $('.jquery_popup').on('click', function (e) {

            // Prevents the default action to be triggered.
            e.preventDefault();
            // Triggering bPopup when click event is fired
            $('#medicine_dialog').bPopup({
                contentContainer: '.content',
                loadUrl: e.target.href
            });
        });
    });

    /* jQury :contains selector case and accented insensitive (https://gist.github.com/oziks/3664787) */
    jQuery.expr[':'].contains = function (a, i, m) {
        var rExps = [{
                re: /[\xC0-\xC6]/g,
                ch: "A"
            }, {
                re: /[\xE0-\xE6]/g,
                ch: "a"
            }, {
                re: /[\xC8-\xCB]/g,
                ch: "E"
            }, {
                re: /[\xE8-\xEB]/g,
                ch: "e"
            }, {
                re: /[\xCC-\xCF]/g,
                ch: "I"
            }, {
                re: /[\xEC-\xEF]/g,
                ch: "i"
            }, {
                re: /[\xD2-\xD6]/g,
                ch: "O"
            }, {
                re: /[\xF2-\xF6]/g,
                ch: "o"
            }, {
                re: /[\xD9-\xDC]/g,
                ch: "U"
            }, {
                re: /[\xF9-\xFC]/g,
                ch: "u"
            }, {
                re: /[\xC7-\xE7]/g,
                ch: "c"
            }, {
                re: /[\xD1]/g,
                ch: "N"
            }, {
                re: /[\xF1]/g,
                ch: "n"
            }
        ];

        var element = $(a).text();
        var search = m[3];

        $.each(rExps, function () {
            element = element.replace(this.re, this.ch);
            search = search.replace(this.re, this.ch);
        });

        return element.toUpperCase()
            .indexOf(search.toUpperCase()) >= 0;
    };

    /* Function to filter the medicines by name */

    function medicineFilter_by_name(list) {
        var input = $('#filterinput');

        $(input)
            .change(function () {
            // Reset the group filter
            $('#filterselect').val(0);
            $(list).find("p.medicine_group").parents('div.group_div').show();
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
        });
    }

    /* Function to filter by group */

    function medicineFilter_by_group(list) {
        var input = $('#filterselect');

        $(input)
            .change(function () {
            // Reset the text filter
            $('#filterinput').val('');
            $(list).find("li.medicine_inn").parents('article').show();

            var filter = $(this).val();
            if (filter) {
                $(list).find("p.medicine_group:not(:Contains(" + filter + "))").parents('div.group_div').hide();
                $(list).find("p.medicine_group:Contains(" + filter + ")").parents('div.group_div').show();
            } else {
                $(list).find("p.medicine_group").parents('div.group_div').show();
            }
            return false;
        })
    }

    /* Function to filter by tag */

    function medicineFilter_by_tag(list) {
        var input = $('#filtertag');

        $(input)
            .change(function () {
            var filter = $(this).val();
            if (this.checked == true) {
                $(list).find("div.medicine_rem:not(:contains(" + filter + "))").parents('article').hide();
                $(list).find("div.medicine_rem:contains(" + filter + ")").parents('article').show();
            } else {
                $(list).find("div.medicine_rem").parents('article').show();
            }
            return false;
        })
    }

    /* Function to filter by location */

    function medicineFilter_by_location(list) {
        var input = document.getElementById('filterlocation');

        $(input)
            .change(function () {
            var filter = $(this).val();
            if (filter) {
                $(list).find("li.medicine_location:not(:contains(" + filter + "))").parents('article').hide();
                $(list).find("li.medicine_location:contains(" + filter + ")").parents('article').show();
            } else {
                $(list).find("li.medicine_location").parents('article').show();
            }
            return false;
        })
    }
    
    /* Function to uncheck the "all" checkbox when others are checked */

    function uncheck(form) {
        var reset_checkbox = $("input[name=allowance-0]");
        var allowance_checkbox = $("input.filtercheck");

        $(reset_checkbox).change(function () {
            if (this.checked == true) {
                // Uncheck the other checkboxes
                $('.filtercheck:checkbox:checked').prop('checked', false);
                $(form).submit();
            }
        })

        $(allowance_checkbox).change(function () {
            if (this.checked == true) {
                // Uncheck of the reset checkbox
                $(reset_checkbox).prop('checked', false);
            }
            // Submit the form anyway
            $(form).submit();
        })
    }

    /* Function to collapse INN in the list on a click event */

    function collapse() {
        var header = $(".medicine_inn_header")

        $(header).click(function () {
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
        })
    }

    /* Function to fix the headers during scrolling */

    function sticky_header() {
        var stickyHeader = $('#medicine_table_header').offset().top + 0;
        $(window).scroll(function () {
            if ($(window).scrollTop() > stickyHeader) {
                var width = $('#medicine_table_header').width();
                $('#medicine_table_header').css({
                    position: 'fixed',
                    top: '0px',
                    width: width
                });
            } else {
                $('#medicine_table_header').css({
                    position: 'static',
                    top: '0px'
                });
            }
        })
    };

    /* Function to scroll up on click on the header */

    function click_header() {
        var header = $('#medicine_table_header');
        $(header).click(function () {
            $("html, body").animate({
                scrollTop: 0
            }, 600);
        })
    }

    /* Function to clear the tex input when clicking on the image */

    function reset_input(){
        var input = $('#filterinput');
        var link = $('#reset_input');

        $(link).click(function (e){
            // Setting the value
            $(input).val('');
            // Calling the filter function
            var event = $.Event("change");
            $(input).trigger(event);
            // Prevents the default action to be triggered.
            e.preventDefault();
        })
    }
})(jQuery);
