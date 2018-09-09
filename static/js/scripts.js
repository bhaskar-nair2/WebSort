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