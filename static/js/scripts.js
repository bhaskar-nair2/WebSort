let filepath = '';
let socket = io.connect();
socket.on('update', function (msg) {
    $('#logger').append(
        '<p>' + msg.text + '</p>'
    );
    if (msg.status === 210) {
        $('#logger').html(
            '<p>Insertion DONE!!!<br>Now Sorting Items</p>'
        );
    }
    if (msg.status === 220) {
        window.alert('REfresh Done!!');
        $('#logger').html(
            '<p>Refresh data completed!!</p>'
        );
    }
    if (msg.status === 200) {
        window.alert('Sorting Done!!');
        $('#downModal').modal('show')
    }
});

socket.on('filepath', function (msg) {
    $('#downloadBTN').prop('disabled', false);
    filepath = msg.text;
    console.log(filepath);
    $('#download').attr('href',filepath)
});
socket.on('NOFILE', function (msg) {
    window.alert('File Error: ' + msg.msg)
});
socket.on('WRONGFILE', function (msg) {
    window.alert('File Error: ' + msg.msg)
});
socket.on('OK', function (msg) {
    $('#logger').html('<p>File Added</p>');
});

function down() {

}

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
        $('#logger').html('<p>Starting a new Search</p>');
        $('#downloadBTN').prop('disabled', true);
        let form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/api/sort',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#logger').html('<p>Sorting Request Sent Successfully!</p>');
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
                $('#logger').html('<p>Refresh Request Sent Successfully!</p>');
            },
        });
    });
});


