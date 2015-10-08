
var marker;
$(document).on('ready', function(){
  console.log('beginning test');
  var map;
  var lat;
  var lon;

//initializing Google Map with draggable marker
  function initialize() {
    var mapOptions = {
      zoom: 15
    };
    map = new google.maps.Map(document.getElementById('map-canvas'),
        mapOptions);

    // Try HTML5 geolocation
    if(navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        var pos = new google.maps.LatLng(position.coords.latitude,
                                         position.coords.longitude);
        lat = position.coords.latitude;
        lon = position.coords.longitude;
        console.log(lat);
        console.log(lon);
        
        marker = new google.maps.Marker({
          draggable: true,
          icon: '/static/img/runnersicon.png',
          position: {'lat':lat,
                      'lng': lon},
          map: map,
          title: 'Drag to move your run location'
        });

        map.setCenter(pos);
      }, function() {
        handleNoGeolocation(true);
      });

    } else {
      // Browser doesn't support Geolocation
      handleNoGeolocation(false);
    }
  }

  google.maps.event.addDomListener(window, 'load', initialize);

  $("#runbutton").on('click', findMatch);
});


function handleNoGeolocation(errorFlag) {
  if (errorFlag) {
    var content = 'Error: The Geolocation service failed.';
  } else {
    var content = 'Error: Your browser doesn\'t support geolocation.';
  }

  var options = {
    map: map,
    position: new google.maps.LatLng(60, 105),
    content: content
  };

  var infowindow = new google.maps.InfoWindow(options);
  map.setCenter(options.position);
}


//evt = metatdata on the event, event.current target for example. 
function findMatch (evt){
  var draggedLat = marker.position.J;
  console.log(draggedLat);
  console.log('test')
  var draggedLon = marker.position.M;
  var matchDuration = $('#match_data').data('duration');
  var matchWaitTime = $('#match_data').data('wait-time');
  var matchScheduled = $('#match_data').data('scheduled');
  var matchDate = $('#match_data').data('date');
  var matchTime = $('#match_data').data('time');
  var inputs = {"lat": draggedLat, "lon": draggedLon, "duration": matchDuration, "wait_time": matchWaitTime, "scheduled": matchScheduled, "date": matchDate, "time": matchTime};

//returning latitude and longitude to server, and changing html to success message.
  $.post('/finding_match', inputs , function(data){
    
    var message = "Great! We got down your details and are texting your potential running buddy";
    $('#runbutton').remove();
    $('#results').html('<div class= "alert alert-success">' + message + '</div>');

  });
};