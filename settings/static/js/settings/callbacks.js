/*jslint indent:4 devel:true*/
/*globals formCallback, jQuery */

(function ($) {
    "use strict";
    /* Callback after import of an update archive. */
    document.formCallback.prototype.importLog = function (data) {
        var table = $("#import-log > table"),
            panel = $("#import-log"),
            i,
            j;

        for (i = 0; i < data.log.length; i += 1) {
            var values = data.log[i].value;
            console.log("Matt", values, data.log[i]);
            for (j = 0; j < values.length; j += 1) {
                if (values[j].type === "error") {
                    table.append("<tr class='form-feedback danger text-danger'><td>" + data.log[i].name + "</td><td>" + values[j].name + "</td><td><b>" + values[j].value + "</b></td></tr>");
                } else {
                    table.append("<tr class='form-feedback'><td>" + data.log[i].name + "</td><td>" + values[j].name + "</td><td>" + values[j].value + "</td></tr>");
                }
            }
        }
        if (data.error) {
            panel.removeClass('panel-success').addClass('panel-danger');
        } else {
            panel.removeClass('panel-danger').addClass('panel-success');
        }
        panel.show();
    };

    /* Callback after import of a PGP Key. */
    document.formCallback.prototype.importKey = function (data) {
        var table = $(".pgp-table > tbody");
        table.append(data.key);
    };

    /* Callback after changing user parameters */
    document.formCallback.prototype.updateUser = function(data){
        console.log("Callback User", data);
    };

}(jQuery));
