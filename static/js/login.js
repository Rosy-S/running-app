$(document).on('ready', function(){

var x = document.getElementById("location-error");
var currentLat;
var currentLon;

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else { 
        x.innerHTML = "Geolocation is not supported by this browser. We cannot match you unless locaiton is enabled :(";
    }
}

function showPosition(position) {

    currentLat = position.coords.latitude;
    currentLon = position.coords.longitude;

    console.log(currentLat, currentLon);

    $.post('/meta-login', {'lat': currentLat, 'lon': currentLon}, function(){
    	console.log("")
    });
};



// $('#location').on('', getLocation);
window.addEventListener("load", getLocation)
});
