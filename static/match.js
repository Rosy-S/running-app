// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see a blank space instead of the map, this
// is probably because you have denied permission for location sharing.
var marker;
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
        


        marker = new google.maps.Marker({
          draggable: true,
          // icon: '/static/img/runnersicon.png',
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
  var draggedLat = marker.position.G;
  var draggedLon = marker.position.K;
  var matchDuration = $('#match_data').data('duration');
  var matchWaitTime = $('#match_data').data('wait-time');
  var matchScheduled = $('#match_data').data('scheduled');
  var matchDate = $('#match_data').data('date');
  var matchTime = $('#match_data').data('time');
  var inputs = {"lat": draggedLat, "lon": draggedLon, "duration": matchDuration, "wait_time": matchWaitTime, "scheduled": matchScheduled, "date": matchDate, "time": matchTime};

  $.post('/finding_match', inputs , function(data){
    // bases for required bootstrap media object functionality
    

    // for (var i = 0; i < data.match.length; i++) {
    var message = "great! We got down your details. Expect a text soon!";
    $('#runbutton').remove();
    $('#results').html('<div class= "alert alert-success">' + message + '</div>');




    //   user_profile_url = '"/matchdetails"';
    //   user_img_src = "/static/img/placeholder.img";
    //   user_name = data.match[i]['user_name'];
    //   description = data.match[i]['duration'];
    //   pace = data.match[i]['pace'];
    //    // miles away now, duration, pace

    //   to_insert = base1 + user_profile_url + base2 + user_img_src + base3 + String(user_name) + "</h4>" + description + pace + "</div>";  
    //   console.log(to_insert);      

    //   $("#result").append(to_insert);         
    // }


    //data.match is a list of objects. for each item in the list, make div id resulsts, and do the selecter that says
    //look for things taht are in the resulsts, and append onto it some code which is a paragraph


    // not finished with this function. Need to plan for the duration of the run, getting the user id of person available, and time ending the run. 
    

  });
};