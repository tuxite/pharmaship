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
 * Filename:    template/js/common.js
 * Description: Common functions
 * Author:      Matthieu Morin
 * Version:     0.2
 * =====================================================================
 */

/* jQuery functions */
(function ($) {

    /* DOM ready */
    $(function () {
        set_dialog();
        open_dialog();
    });
    
    /* Settings of the layout */
    $(document).ready(function () {
        $("body").layout({
            north: {
                closable: false,
            },
            west: {
                size: "215",
            },
        });
    });

    /* Function for passing X-Ref protection */
    // Code from Django documentation
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false,
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    /* jQuery :contains selector case and accented insensitive (https://gist.github.com/oziks/3664787) */
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
    }

    /* Function to operate dialog */
    function set_dialog() {
        $("#dialog").dialog({
            modal: true,
            autoOpen: false,
            height: "auto",
            width: "auto",
            buttons: {
                "Delete all items": function () {
                    $(this).dialog("close");
                },
                Cancel: function () {
                    $(this).dialog("close");
                }
            }
        });
    }

    /* Function to open a dialog */
    function open_dialog() {
        /* jQuery wrapper for handling clicks to open popups */
        $(document).on('click', '.jquery_popup', function (e) {

            // Prevents the default action to be triggered.
            e.preventDefault();

            // Ajax loader and parser for Dialog
            $.ajax({
                url: e.target.href,
                success: function (data) {
                    $("#dialog-text").html(data.text);
                    $("#dialog-foot").html(data.foot_text);
                    $("#dialog-form").html("<table>" + data.form + "</table>");
                    $("#dialog").dialog("option", "title", data.title);
                    $("#dialog").dialog("option", "buttons", [
                        {
                            text: data.button_KO,
                            click: function () {
                                $(this).dialog("close");
                            }
                        },
                        {
                            text: data.button_OK,
                            click: function () {
                                // Delete all errors
                                $(".form-error").removeClass("form-error");
                                $(".form-label-error").removeClass("form-label-error");
                                $(".form-error-msg").remove();
                                // We submit the form
                                var form = $("#dialog > form");
                                $.ajax({
                                    type: "POST",
                                    url: data.url,
                                    data: form.serialize(),
                                    success: function (data) {
                                        // Here, reload concerned part of the body
                                        // Note: the dialog_callback must be defined in the concerned JS file.
                                        dialog_callback(data);
                                        // Then close the dialog
                                        $("#dialog").dialog("close");
                                    },
                                    error: function (data) {
                                        console.log(data.responseText);
                                        // Process the error message
                                        var errors = JSON.parse(data.responseText);
                                        for (field in errors) {
                                            var input = $("[name*='" + field + "']");
                                            // Cosmetics
                                            input.addClass("form-error");
                                            $("label[for='" + input.attr('id') + "']").addClass("form-label-error");
                                            // Append the error message
                                            var tr = input.parent().parent();
                                            tr.append("<td class='form-error-msg'>" + errors[field] + "</td>");
                                        }
                                    },
                                });
                                return false;
                            }
                        }
                        ]);
                    $("#dialog").dialog("open");
                }
            });
        });
    }

})(jQuery);