let socket = io.connect();
socket.on('update', function (msg) {
    $('#logger').append(
        '<p>' + msg.current + '</p>'
    );
    if (msg.current === 'OVER') {
        $('#logger').html(
            '<p>Insertion DONE!!!<br>Now Sorting Items</p>'
        );
    }
});

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

$(function () {
    $('#upload-file-btn').click(function () {
        let form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/api/sort',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#logger').append('<p>Sorting Request Sent Successfully!</p>');
            },
        });

    });
});

$(function () {
    $('#refresh-file-btn').click(function () {
        let form_data = new FormData($('#refresh-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/api/refresh',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#logger').append('<p>Refresh Request Sent Successfully!</p>');
            },
        });
    });
});


