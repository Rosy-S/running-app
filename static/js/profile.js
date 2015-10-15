$(document).on('ready', function(){

	var options = {
		responsive: true,
	};

	// Make Donut Chart of percent of different types of Melons
	var ctx_donut = $("#donutChart").get(0).getContext("2d");

	$.get("/chart_stuff", function(data){
		var json_data = $.parseJSON(data);
		var myDonutChart = new Chart(ctx_donut).Doughnut(json_data, options);
		$('#donutLegend').get(0).innerHTML = myDonutChart.generateLegend();
	});

	// Make Line Chart of Melon Sales over time
	var ctx_line = $("#lineChart").get(0).getContext("2d");

	$.get("/chart_stuff2", function(data){
		var json_data = $.parseJSON(data);
		var myLineChart = new Chart(ctx_line).Line(json_data, options);
		$("#lineLegend").get(0).innerHTML = myLineChart.generateLegend();
	});








});
