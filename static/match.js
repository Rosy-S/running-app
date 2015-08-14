// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see a blank space instead of the map, this
// is probably because you have denied permission for location sharing.
$(document).on('ready', function(){
console.log('beginning test');
var map;
var lat;
var lon;

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
      


      var infowindow = new google.maps.InfoWindow({
        map: map,
        position: pos,
        content: 'Location found using HTML5.'
      });
      var matchDuration = $('#match_data').data('duration');
      var matchWaitTime = $('#match_data').data('wait-time');
      var inputs = {"lat": lat, "lon": lon, "duration": matchDuration, "wait_time": matchWaitTime};

      $.post('/finding_match', inputs , function(data){
        console.log("data: ", data);
        console.log("data match", data.match[0]);
        console.log("data length: ", data.match.length);

        var object = data.match;
        console.log("object duration: ", object[0]['duration'])

        for (var i = 0; i < data.match.length; i++) {

          $("#result").append('<li>' + object[i]['duration'] + '</li>');         
        }


        //data.match is a list of objects. for each item in the list, make div id resulsts, and do the selecter that says
        //look for things taht are in the resulsts, and append onto it some code which is a paragraph


        // not finished with this function. Need to plan for the duration of the run, getting the user id of person available, and time ending the run. 
        

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



google.maps.event.addDomListener(window, 'load', initialize);
});