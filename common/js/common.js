/* jQuery functions */
(function ($) {
    /* DOM ready */
    $(function () {
        /* Generic form controls and feedbacks. */
        forms_controls();

        /* Activation of the tooltips */
        $('.bt-tooltip').tooltip();

        /* Activation of the fileinputs */
        $("input[type=file]").fileinput({
            'showUpload': false,
            'showPreview': false,
            'browseLabel': '',
            'removeLabel': '',
            maxFileCount: 1
        });

        /* Reset of the modals on hiding. */
        $('#action_modal').on('hidden.bs.modal', function (e) {
            // Reset the modal
            $('#action_modal').removeData();
        });
        $('#lightbox').on('hidden.bs.lightbox', function (e) {
            // Reset the modal
            $('#lightbox').removeData();
        });
    });

    /* Function for passing X-Ref protection */
    // Code from Django documentation
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
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

    /* Function to set the controls of the forms */
    function forms_controls() {
        $(".input_erase").click(function (event) {
            $(event.target).parents("div.input-group:first").find("input:first").val('');
        });

        $(document).on("submit", "form", function(event){
            form = $(this);
            // Reset the form
            $('.alert').hide();
            form.find('.has-error').removeClass('has-error');
            $('.form-feedback').remove();

            // Overriding the default
            event.preventDefault();

            // Set the button
            button = $(event.target).find('button[type=submit]');
            button.button('loading');
            // Ajax Call
            form.ajaxSubmit({
                type: "POST",
                url: form.prop('action'),
                success: function (data) {
                    // Reset the button
                    button.button('reset');
                    // Return a success message
                    button.parent().append("<span class='text-success form-feedback'><b>"+data.success+"</b></span>");
                    // Get the callback
                    var callback = form.attr("data-form-callback");
                    if (callback != undefined){
                        // We have a callback, try to load it.
                        console.log("Form Callback:", callback);
                        if (callback in document.formCallback.prototype){
                            eval('document.formCallback.prototype.'+callback+'(data)');
                        }
                    }
                },
                error: function (data) {
                    console.log(data);
                    // Reset first the button
                    button.button('reset');
                    // Check if this is a server error
                    if (data.status >= 500) {
                        button.parent().append("<span class='text-danger form-feedback'><b>Internal Server Error</b></span>");
                        return false;
                    }
                    // Process the error message
                    var errors = JSON.parse(data.responseText);
                    for (field in errors.details) {
                        // Cosmetics
                        // Use the selector class=' ' to match bootstrap-forms input parent
                        // even with some plugins modifying the appearance of the input.
                        var input = form.find("[name*='" + field + "']"),
                            parent = input.parents("div[class=' ']:first");
                        parent.addClass("has-error");
                        parent.append('<p class="text-danger form-feedback">'+errors.details[field]+'</p>');
                    };

                    // Return an error message
                    button.parent().append("<span class='text-danger form-feedback'><b>"+errors.error+"</b></span>");
                    // Get the error callback
                    var callback = form.attr("data-form-error-callback");
                    if (callback != undefined){
                        // We have a callback, try to load it.
                        console.log("Form Error Callback:", callback);
                        if (callback in document.formCallback.prototype){
                            eval('document.formCallback.prototype.'+callback+'(errors)');
                        }
                    }
                },
            });
        });
    }
    /* Global variable to set different callback prototypes for the forms. */
    document.formCallback = function(){};

})(jQuery);
