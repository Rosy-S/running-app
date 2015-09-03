from jinja2 import StrictUndefined
from twilio import twiml
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from twilio.rest import TwilioRestClient

from model import connect_to_db, db, User, UserRun, Match

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
	str_asker_id = str(asker_id)
	# send a text to person who did the run app (test in this case) to check their email box.

	client = TwilioRestClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
	message=client.messages.create(from_=os.environ['TWILLIO_NUMBER'], to=recipient_number, body=("Hey there! %s wants to go on the run you posted! Login and check your ibox to confirm!") % (asker_name))

	flash("You have just chosen to run with " + recipient_name)


	return redirect("/users/" + str_asker_id + "/" + asker_name)
@app.route('/finding_match', methods=["POST"])
def finding_match(): 
	""" Route to handle ajax request to get user's prefered run location as lat and lng coordinates"""

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
		if (match.run.time_end > datetime.datetime.now()) and (match.accepted != False): 
			final_matches.append(match)
	jinja_js_content ={} # preparing to pass information to jinja and javascript so it can be displayed
	
	#If no matches exist for a user, display such message. Otherwise, append alternate message and objects storing data we need to display to user
	if not final_matches: 
		jinja_js_content['message'] = "No matches for now. Feel free to go to your profile and make as many matches as you would like!"
	else: 
		jinja_js_content['message'] = "You have %d requests to run!" % (len(final_matches))
		jinja_js_content['matches'] = []
		for match in final_matches:
			run_info = match.run 
			asker_info = User.query.get(match.asker_id)
			# Making a list of tuples match, run and usser objects corresponding to that match that the recipeint made.
			jinja_js_content['matches'].append((match, run_info, asker_info))
	return render_template("inbox.html", jinja_content=jinja_js_content)


@app.route('/make_run/confirmation/<int:match_id>')
def run_confirmation(match_id): 
	""" Handling an accepted match on the Match table"""

	# changing status of accepted match to True
	accepted_match = Match.query.get(match_id)
	accepted_match.accepted = True
	db.session.add(accepted_match)
	db.session.commit()

	time_start = accepted_match.run.time_start.strftime("%B %d, %Y at %I:%M %p")
	# getting phone numbers for respective asker and recipient
	asker_number = User.query.get(accepted_match.asker_id).phone
	asker_name = accepted_match.user.user_name
	recipeint_number = User.query.get(accepted_match.recipient_id).phone 
	recipient_name = User.query.get(accepted_match.recipient_id).user_name
	client = TwilioRestClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
	message=client.messages.create(from_=os.environ['TWILLIO_NUMBER'], to=asker_number, body=("Hello! %s got the message that you want to run with them! You are running with them on %s!") % (recipient_name, time_start))
	user_id = str(session.get('user_id'))
	return redirect('/inbox/requests/' + user_id)


@app.route('/make_run/no-thanks/<int:match_id>')
def run_rejection(match_id):
	rejected_match = Match.query.get(match_id)
	rejected_match.accepted = False
	db.session.add(rejected_match)
	db.session.commit()
	user_id = str(session.get('user_id'))

	#handling rejection
	return redirect('/inbox/requests/' + user_id)



@app.route('/test')
def test(): 
	return render_template('test.html')




if __name__ == "__main__":
	# We have to set debug=True here, since it has to be True at the point
	# that we invoke the DebugToolbarExtension
	app.debug = True

	connect_to_db(app)

	# # Use the DebugToolbar
	# DebugToolbarExtension(app)

	app.run()