function getPaper() {
    var displayElement = document.getElementById('displayElement');
    var editionWithCity = document.getElementById('edition').value.split(':');
    var editionNumber = editionWithCity[0];
    var editionCity = editionWithCity[1];

    displayElement.innerHTML = 
    `<div>
        Fetching ePaper for ${editionCity}... This may take 3-5 minutes... Please wait...
    </div>
    <div class="loader">Loading...</div>`;

    fetch(`http://${window.location.host}/api/deccan?edition=${editionNumber}`)
    .then(response => { 
        return response.json();
    }).then(data => {
        if (data['response']) {
            var file_name = data['file_name']
            window.location.href = `/locate/${file_name}`;
        }
        else {
            var msg = data['message']
            var errors = data['data']
            displayElement.innerHTML = `<h3>${msg}</h3><br><p>${errors}</p>`
        }
    })

    console.log("waiting for API");
}