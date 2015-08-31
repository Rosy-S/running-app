var declineButton = $(".btn-danger")

var displayTime = $(".timestart");
var moreDisplayTime = moment(displayTime, 'YYYY-MMMM-DD HH:mm:ss');
console.log(moreDisplayTime);
var finalTime = 
displayTime.innerHTML = moreDisplayTime.format('MMM/DD/YY, hh:mm');
console.log("The display time: ", displayTime);
