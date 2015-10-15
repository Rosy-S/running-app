var map;
var markers;
var markerObjects;
var infos = [];

var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

function formatAMPM(date) {
  var month = monthNames[date.getMonth()];
  var day = date.getDate();
  var year = date.getFullYear();
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var ampm = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0'+minutes : minutes;
  var strTime = month + "/" + day + "/" + year + " at " + hours + ':' + minutes + ' ' + ampm;
  return strTime;
}

// Initializing Google Map and placing markers/infoWindow
function initMap() {

  	map = new google.maps.Map(document.getElementById('map'), {
    	zoom: 12,
    	center: {lat: 37.773972, lng: -122.431297}
  	});


	// Data for the markers consisting of a name, a LatLng and a Index for the
	// order in which these markers should display on top of each other.
	markers = $(".marker");
	markerObjects = [];
	for(var i = 0; i < markers.length; i++){
		var markerData = $(markers[i]).data();

    var timeDate = new Date(markerData.startdate);
  
    var current = new Date();

    if (current > timeDate){
      timeDate = "<span style='color: red'><strong>Now!</strong></span>";
    } else {
      timeDate = formatAMPM(timeDate);
  
    }


		var contentString = (
			'<div id="content">'+
      		'<div id="siteNotice">'+
      		'</div>'+
      		'<h3 id="firstHeading" class="firstHeading">' + 'Run Details for ' + markerData.name + '</h3>' + 
      		'<div id="bodyContent">'+
            '<ul><li> Time of run: ' + timeDate + '</li>' +
            '<li> Duration: ' + markerData.duration + ' minutes</li>' +
            '<li> Runner mile time: ' + markerData.miletime + ' min per mile' + '</li>'  +  
      		'</ul></div>' +
      		'</div>');

		//creating Info Window
		var infoWindow = new google.maps.InfoWindow({
			content: contentString
		});

		//putting Info Windows in one place
		infos.push(infoWindow)


  	var marker = new google.maps.Marker({
    	position: {lat: markerData['lat'], lng: markerData['lon']},
    	map: map,
    	animation: google.maps.Animation.DROP,
    	icon: '/static/img/runnersicon.png',
    	title: "map of possible runs",
    	// zIndex: beach[3]
  	});

  	// adding event listeners for our markers
  	bindinfoWindow(marker, map, infoWindow, contentString);
  } // End of the for loop

} // End of inItMap function.

// Setting info windows to appropriate markers
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


