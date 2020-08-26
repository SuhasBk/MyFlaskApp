var fileName = '';
var timer;
var counter = 0;

function getPaper() {
    var displayElement = document.getElementById('displayElement');
    var editionWithCity = document.getElementById('edition').value.split(':');
    var editionNumber = editionWithCity[0];
    var editionCity = editionWithCity[1];

    displayElement.innerHTML = 
    `<div class="info">
        Please wait...<br>Fetching ePaper for ${editionCity}... This may take 3-5 minutes... Go get coffee or something!<br>
    </div>
    <div class="loader">Loading...</div>`;

    fetch(`http://${window.location.host}/api/deccan?edition=${editionNumber}`)
    .then(response => { 
        return response.json();
    })
    .then(data => {
        fileName = data['response'];
        timer = setInterval(checkIfDone, 20000);
    });

    console.log("waiting for API");
}

function checkIfDone() {
    fetch(`http://${window.location.host}/api/find?file=${fileName}`)
    .then(response => {
        return response.json();
    })
    .then(data => {
        if (data['response']) {
            clearInterval(timer);
            window.location.href = `/locate/${fileName}`;
        }
        else {
            if (data['errors']) {
                displayError(data['errors']);
            } else {
                console.log('Still downloading... please wait...');
                if (counter < 10) {
                    counter++;
                }
                else {
                    displayError('Unexpected Error. Cant proceed further :(');
                }
            }
        }
    })
}

function displayError(errors) {
    clearInterval(timer);
    displayElement.innerHTML = `<h2>${errors}</h2><br>`;
}