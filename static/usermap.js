
var map;
var markers;
var markerObjects;
var infos = [];

// $(document).on('ready', function(){
function initMap() {

  	map = new google.maps.Map(document.getElementById('map'), {
    	zoom: 12,
    	center: {lat: 37.773972, lng: -122.431297}
  	});

  // setMarkers(map);

	// Data for the markers consisting of a name, a LatLng and a Index for the
	// order in which these markers should display on top of each other.
	markers = $(".marker");
	markerObjects = [];
	for(var i = 0; i < markers.length; i++){
		var markerData = $(markers[i]).data();

		var contentString = (
			'<div id="content">'+
      		'<div id="siteNotice">'+
      		'</div>'+
      		'<h1 id="firstHeading" class="firstHeading">' + 'Run Details for ' + markerData.name + '</h1>' + 
      		'<div id="bodyContent">'+
      			'<ul><li> Duration: ' + markerData.duration + '</li>' +
      			'<li> Runner mile time: ' + markerData.miletime + ' min per mile' + '</li>'  +  
      		'</ul></div>' +
      		'</div>');

		//creating Info Window
		var infoWindow = new google.maps.InfoWindow({
			content: contentString
		});
		console.log("INFO WINDOW: ");
		console.log(infoWindow);
		//putting Info Windows in one place
		infos.push(infoWindow)

      
		// markerObjects.push(data);

	// }

	// for (var i = 0; i <= markerObjects.length; i++) {

		//making our markers
    	// var mapData = markerObjects[i];
    	var marker = new google.maps.Marker({
      	position: {lat: markerData['lat'], lng: markerData['lon']},
      	map: map,
      	animation: google.maps.Animation.DROP,
      	// icon: image,
      	// shape: shape,
      	title: "map of possible runs",
      	// zIndex: beach[3]
    	});

    	// adding event listeners for our markers
    	bindinfoWindow(marker, map, infoWindow, contentString);
  	} // End of the for loop


} // End of inItMap function.

function bindinfoWindow(marker, map, infoWindow, html) {
	google.maps.event.addListener(marker, 'click', function() {
// Set infoWindow content and open it when user clicks.
closeInfos();
infoWindow.setContent(html);
infoWindow.open(map, marker);
});
}

function closeInfos() {
        for (i = 0; i < infos.length; i++) {
           	infos[i].close();
        }
}

google.maps.event.addDomListener(window, 'load', initMap);

