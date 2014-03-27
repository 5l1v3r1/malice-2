/**
 * Created by work on 12/23/13.
 */

var log;

log = function (status) {
    return $("#status").html(status);
};

$(function () {
    var form;
    $("#upload_button").click(function () {
        return $("input[type=file]").click();
    });
    form = $("#upload_form");
    return form.fileupload({
        autoUpload: true,
        dataType: "txt",
        add: function (event, data) {
            log("fetching params");
            return $.get("{{ url_for('params') }}").done(function (params) {
                form.find('input[name=key]').val(params.key);
                form.find('input[name=policy]').val(params.policy);
                form.find('input[name=signature]').val(params.signature);
                return data.submit();
            });
        },
        send: function (event, data) {
            return log("sending");
        },
        progress: function (event, data) {
            return $("#progress_bar").css("width", "" + (Math.round((event.loaded / event.total) * 1000) / 10) + "%");
        },
        fail: function (event, data) {
            return log("failure");
        },
        success: function (event, data) {
            return log("success");
        },
        done: function (event, data) {
            return log("done");
        }
    });
});