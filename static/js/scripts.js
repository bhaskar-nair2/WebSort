function app() {
    $.getJSON('/api/test', function (data) {
        for (let i = 0; i < Object.keys(data).length; i++) {
            console.log(data[i]);
            $('.inner').append(
                "<p>" + data[i].name + "</p>"
            )
        }
    })
}

$(function() {
    $('#upload-file-btn').click(function() {
        let form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/api/refresh',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Success!');
            },
        });
    });
});