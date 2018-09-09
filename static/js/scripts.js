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

$('form').on('submit', function () {
    event.stopPropagation(); // Stop stuff happening
    event.preventDefault(); // Totally stop stuff happening
    let file = document.getElementById('fileBox').files[0]; //Files[0] = 1st file
    let reader = new FileReader();
    reader.readAsText(file, 'UTF-8');
    reader.onload = shipOff;

    function shipOff(event) {
        let result = event.target.result;
        let fileName = document.getElementById('fileBox').files[0].name; //Should be 'picture.jpg'
        $.post('/api/file', {data: result, name: fileName});
    }
});