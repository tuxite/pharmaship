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
 * Filename:    template/js/home.js
 * Description: JS for home view
 * Author:      Matthieu Morin
 * Version:     0.1
 * =====================================================================
 */

/* jQuery functions */
;
(function ($) {

    /* DOM ready */
    $(function () {
        collapse();

        /* Hide all panels on load */
        $("div.more").hide();

    });

/* Function to collapse some details in the page on a click event */

    function collapse() {
        var header = $("li.top")

        $(header).click(function () {
            var panel = $(this).parents('div.line').find("div.more");
            // Getting the previous state
            var state = panel.is(":hidden");
            // Resetting the display
            $('div.line').removeClass("active");
            // Resetting the display
            $("div.more").hide();
            // Any change?
            if (state == true) {
                // Change the class
                $(this).parents('div.line').addClass("active");
                // Show the panel
                panel.show();
            }
        })
    };
})(jQuery);
