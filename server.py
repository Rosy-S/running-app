from jinja2 import StrictUndefined
from twilio import twiml
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from twilio.rest import TwilioRestClient

from model import connect_to_db, db, User, UserRun, Match
from messaging import *

import json
import datetime
import re, math
import os



CONSTANT_MI_DEGREE = 69


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "MuchSecretWow"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():

	return render_template("homepage.html")

########REGISTRATION #####################################

@app.route('/register', methods=['GET'])
def register_form():
	"""Show form for user signup."""

	return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
	"""Process registration."""

	# Get form variables
	user_name = request.form["user_name"]
	email = request.form["email"]
	password = request.form["password"]
	mile_time = request.form["mile_time"]
	phone = request.form["phone"]


	new_user = User(user_name=user_name, password=password, email=email, mile_time=mile_time, phone=phone)

	db.session.add(new_user)
	db.session.commit()

	flash("User %s added." % user_name)

	user = new_user 
	session["user_id"] = user.user_id
	session["user_name"] = user.user_name

	return redirect("/login")

	
################LOGING IN ROUTES #####################################

@app.route('/login', methods=['GET'])
def login_form():
	"""Show login form."""

	return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
	"""Process login."""

	# Get form variables
	email = request.form["email"]
	password = request.form["password"]

	user = User.query.filter_by(email=email).first()

	if not user:
		flash("No such user! Try logging in again")
		return redirect("/login")

	if user.password != password:
		flash("Incorrect password")
		return redirect("/login")

	session["user_id"] = user.user_id
	session["user_name"] = user.user_name

	flash("Logged in")
	return redirect("/users/%s/%s" % (user.user_id, user.user_name))

@app.route('/meta-login', methods=['POST'])
def function(): 

	# meta-login required to get user's latitude and longitude coordinates upon signing in.
	lat = request.form.get('lat')
	lon = request.form.get('lon')
	session['lat']  = lat
	session['lon'] = lon 
	return "success"


@app.route('/logout')
def logout():
	"""Log out."""

	session.clear()
	flash("Logged Out.")
	return redirect("/")


########USER LOGGED IN ROUTES########################

@app.route("/users/<int:user_id>/<user_name>")
def user_detail(user_id, user_name):
	"""Show potential runs given a user."""

	current_user = User.query.get(session['user_id'])
	current_user_id = current_user.user_id 
	current_user_pace = (current_user.mile_time)
	user_lat = session['lat']
	user_lon = session['lon']
	# check for expired runs and change active status to False: 
	expired_runs = UserRun.query.filter(UserRun.time_end < datetime.datetime.now()).all()
	if expired_runs: 
		for expired_run in expired_runs: 
			expired_run.active_status = False
		db.session.commit()

	# check for active runs that are not the user's run and store them in potetial_runs variable
	potential_runs = UserRun.query.filter(UserRun.active_status == True, UserRun.user1 != current_user_id).all()
	final_runs = []
	for run in potential_runs: 
		# if the pace of the user is within 2 min of each other: 
		if abs(current_user_pace - run.user.mile_time)  < 2: 
			# if the duration is within 10 min of each other: 
			run_lon = float(run.lon_coordinates)
			run_lat = float(run.lat_coordinates)
			degree_distance = math.sqrt(((float(user_lat) - run_lat)**2) + ((float(user_lon) - run_lon)**2))
			miles_distance = degree_distance * CONSTANT_MI_DEGREE
			# using distance equation, if distance is within 5 miles from the other run, store run in final_runs variable
			if miles_distance < 5: 
				final_runs.append((run, miles_distance))


	return render_template("user.html", user_id=user_id, runs=final_runs, user_name=user_name) 

@app.route('/<int:user_id>/<string:user_name>/schedule_run', methods=['POST'])
def scheduling_run(user_id, user_name): 
	""" Step 1 out of 2 for making a run for a user """
	duration = request.form.get("amount")
	wait_time = request.form.get("time_amount")
	scheduled = request.form.get('scheduled')
	date = request.form.get("datepicker")
	time = request.form.get("time")
	if scheduled == "True": 
		wait_time = 0        
	# date and time for non-scheduled runs is going to be None.
	return render_template('schedule_run.html', duration=duration, wait_time=wait_time, scheduled=scheduled, date=date, time=time)


@app.route("/choose-run/<int:run_id>")
def choose_run(run_id):
	""" Making a match when a user chooses a run and sending a text notifying the maker of the run"""
	
	asker_id = session['user_id']
	asker_name = User.query.get(asker_id).user_name
	recipient = UserRun.query.get(run_id)
	recipient_id = recipient.user1
	recipient_number = User.query.get(recipient_id).phone
	recipient_name = User.query.get(recipient_id).user_name
	new_match = Match(asker_id=session['user_id'], recipient_id=recipient_id, run_id=run_id, asked_at=datetime.datetime.now())
	db.session.add(new_match)
	db.session.commit()
	match_info = new_match.make_match_dictionary()
	match_info['recipient_name'] = recipient.user.user_name
	match_id = int(match_info['match_id'])
	str_asker_id = str(asker_id)
	# send a text to person who did the run app to check their email box or respond 'YES' with the match_id.
	choosing_run(recipient_number, asker_name, match_id)

	flash("You have just chosen to run with " + recipient_name)
	return redirect("/users/" + str_asker_id + "/" + asker_name)

@app.route('/finding_match', methods=["POST"])
def finding_match(): 
	""" Route to handle ajax request to get user's prefered run location as lat and lng coordinates"""
	print "the values", request.form.values
	# Adding/updating a match column for the user currently in the session.
	lat = float(request.form.get('lat'))
	lon = float(request.form.get('lon'))
	duration = request.form.get("duration")
	# RegEx needed to parse user's input
	duration = int(re.sub("[^0-9]", "", duration))
	wait_time = request.form.get("wait_time")  
	wait_time = int(re.sub("[^0-9]", "", wait_time))
	scheduled = request.form.get("scheduled")
	date = request.form.get('date')
	time = request.form.get('time')

	# if the user wants to "run now", time start is current time. Otherwise parse form datetime information to store it in time_start
	if scheduled == "False": 
		time_start = datetime.datetime.now()
	else: 
		full_time = date + "/" + time[:2] + '/' + time[3:5] +  time[6:8]
		time_start = datetime.datetime.strptime(full_time, "%m/%d/%Y/%I/%M%p")
	
	time_end = time_start + datetime.timedelta(minutes=wait_time)
	existing_run = UserRun.query.filter_by(user1=session['user_id']).first()

	if not existing_run:
		new_match = UserRun(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_start=time_start, time_end=time_end, duration=duration)
		db.session.add(new_match)
		db.session.commit()
	else: 
		lst_of_runs = UserRun.query.filter_by(user1=session['user_id']).all()
		# deactivating user runs that have expired at this point in time.
		for run in lst_of_runs:
			if run.time_end  < datetime.datetime.now(): 
				run.active_status = False
				db.session.commit()
		new_match = UserRun(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_start=time_start, time_end=time_end, duration=duration)
		db.session.add(new_match)
		db.session.commit()
		
	return jsonify({'new_match_id': new_match.run_id})

@app.route('/inbox/requests/<int:user_id>')
def show_requests(user_id): 
	""" Showing current user potential matches. Users can decline (deactivating the match) or accept (completing the match) """

	# query Match database for matches pertaining to the user currently logged in
	preliminary_matches = Match.query.filter(Match.recipient_id == session['user_id']).all()
	final_matches = []

	# filtetering preliminary_matches if they are not already deactivated or expired
	for match in preliminary_matches: 
		if (match.run.time_end > datetime.datetime.now()) and (match.accepted == None): 
			final_matches.append(match)
	jinja_js_content ={} # preparing to pass information to jinja and javascript so it can be displayed
	
	#If no matches exist for a user, display such message. Otherwise, append alternate message and objects storing data we need to display to user
	if not final_matches: 
		jinja_js_content['message'] = "You have no pending matches for now. Feel free to go to your profile and make as many matches as you would like!"
	else: 
		jinja_js_content['message'] = "You have %d new requests to run!" % (len(final_matches))
		jinja_js_content['matches'] = []
		for match in final_matches:
			run_info = match.run 
			asker_info = User.query.get(match.asker_id)
			# Making a list of tuples match, run and usser objects corresponding to that match that the recipeint made.
			jinja_js_content['matches'].append((match, run_info, asker_info))
	return render_template("inbox.html", jinja_content=jinja_js_content)


@app.route('/make_run/confirmation/<int:match_id>', methods=["GET"])
def run_confirmation(match_id): 
	""" Handling an accepted match on the Match table"""
	# changing status of accepted match to True
	accepted_match = Match.query.get(match_id)
	accepted_match.accepted = True
	accepted_match.run.active_status = False
	db.session.add(accepted_match)
	db.session.commit()

	time_start = accepted_match.run.time_start.strftime("%B %d, %Y at %I:%M %p")
	# getting phone numbers for respective asker and recipient
	asker_number = User.query.get(accepted_match.asker_id).phone
	asker_name = accepted_match.user.user_name
	recipeint_number = User.query.get(accepted_match.recipient_id).phone 
	recipient_name = User.query.get(accepted_match.recipient_id).user_name
	confirmation_text(asker_number, recipient_name, time_start)
	user_id = str(session.get('user_id'))
	return redirect('/inbox/requests/' + user_id)


@app.route('/make_run/no-thanks/<int:match_id>')
def run_rejection(match_id):
	rejected_match = Match.query.get(match_id)
	rejected_match.accepted = False
	rejected_match.run.active_status = False
	db.session.add(rejected_match)
	db.session.commit()
	user_id = str(session.get('user_id'))

	#handling rejection
	return redirect('/inbox/requests/' + user_id)


###################### USER PROFILE ROUTES ############################################

@app.route("/users/profile/<int:user_id>/<string:user_name>")
def user_profile(user_id, user_name):
	return render_template("profile.html")
	

@app.route('/chart_stuff')
def chart_stuff(): 
	all_recipient_matches = Match.query.filter(Match.recipient_id == session['user_id'], Match.accepted == True).all()
	all_asker_matches = Match.query.filter(Match.asker_id == session['user_id'], Match.accepted == True).all()
	frequency_dict = {}
	# Storing the matches that the user in session was asked on
	for match in all_recipient_matches: 
		name = match.asker_id
		if name in frequency_dict: 
			frequency_dict[name] += 1
		else: 
			frequency_dict[name] = 1

	# Storing the mathes that the user in session asked others
	# Frequency dict now has other runner's id as a key and the amount of times the user in session ran with them.
	for match in all_asker_matches: 
		name = match.recipient_id
		if name in frequency_dict: 
			frequency_dict[name] += 1
		else: 
			frequency_dict[name] = 1

	print "frequency_dict: ",  frequency_dict
	# data_list_of_dicts  []
	# for key, value in in frequency_dict.iteritems(): 
	# 	data_list_of_dicts.append(
	data_list_of_dicts = [
		{
			"value": 3,
			"color": "#F7464A",
			"highlight": "#FF5A5E",
			"label": "test"
		},
		{
			"value": 5,
			"color": "#46BFBD",
			"label": "Crenshaw"
		},
		{
			"value": 2,
			"color": "#FDB45C",
			
			"label": "Yellow Watermelon"
		}
	]
	return json.dumps(data_list_of_dicts)

@app.route('/chart_stuff2')
def melon_data1():
	data_dict =  {
		"labels": ["January", "February", "March", "April", "May", "June", "July"],
		"datasets": [
			{
				"label": "Watermelon",
				"fillColor": "rgba(220,220,220,0.2)",
				"strokeColor": "rgba(220,220,220,1)",
				"pointColor": "rgba(220,220,220,1)",
				"pointStrokeColor": "#fff",
				"pointHighlightFill": "#fff",
				"pointHighlightStroke": "rgba(220,220,220,1)",
				"data": [65, 59, 80, 81, 56, 55, 40]
			},
			{
				"label": "Cantaloupe",
				"fillColor": "rgba(151,187,205,0.2)",
				"strokeColor": "rgba(151,187,205,1)",
				"pointColor": "rgba(151,187,205,1)",
				"pointStrokeColor": "#fff",
				"pointHighlightFill": "#fff",
				"pointHighlightStroke": "rgba(151,187,205,1)",
				"data": [28, 48, 40, 19, 86, 27, 90]
			}
		]
	}
	return json.dumps(data_dict)




#################### RESPOND BY TEXTING FEATURES ##################################
@app.route('/incoming_texts', methods=['POST'])
def test(): 
	raw_from_number=request.values.get('From')
	from_number = int(raw_from_number[2:])
	incoming_message=request.values.get('Body')
	incoming_message = incoming_message.split(' ') 
	if len(incoming_message) > 1: 
		match_id = int(incoming_message[0])
		match_object = Match.query.get(match_id)
		recipient_number = int(User.query.get(match_object.recipient_id).phone)
		recipient_name = str(User.query.get(match_object.recipient_id).user_name)
		if str(incoming_message[1]) in ['Yes', 'YES', 'yes'] and from_number == recipient_number: 
			if match_object.accepted == None: 
				match_object.accepted = True
				match_object.run.active_status = False
				db.session.add(match_object)
				db.session.commit()
				time_start = str(match_object.run.time_start.strftime("%B %d, %Y at %I:%M %p"))
				message = "Great! You and your running buddy are all set to run! You are running on %s." % (time_start)
				confirmation_text(recipient_number, recipient_name, time_start)
			elif match_object.accepted == True: 
				message = "This match has already been made and your run buddy has been contacted"
			elif match_object.accepted == False: 
				message = "You have already rejected this match"
		elif str(incoming_message[1]) in ['No', 'NO', 'no'] and from_number == recipient_number: 
			match_object.accepted = False 
			message = "Gotcha, we will keep this run open until the expiration time."
		else: 
			message = "Sorry, it seems you typed something I could not understand. Please try again with the number specified in the text, and then a 'yes' or 'no'"
	else: 
		message = "Sorry, it seems you typed something I could not compute. Please try again with the number specified in the text, and then a 'yes' or 'no'"
	resp = twiml.Response()
	resp.message(message)
	print"**************************************************"
	return str(resp)




if __name__ == "__main__":
	# We have to set debug=True here, since it has to be True at the point
	# that we invoke the DebugToolbarExtension
	app.debug = True

	connect_to_db(app)

	# # Use the DebugToolbar
	# DebugToolbarExtension(app)

	app.run()