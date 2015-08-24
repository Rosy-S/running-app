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
    """Show info about user."""

    current_user = User.query.get(session['user_id'])
    current_user_id = current_user.user_id 
    current_user_pace = (current_user.mile_time)
    user_lat = session['lat']
    user_lon = session['lon']
    # check for expired runs: 
    expired_runs = UserRun.query.filter(UserRun.time_end < datetime.datetime.now()).all()
    if expired_runs: 
        for expired_run in expired_runs: 
            expired_run.active_status = False
        db.session.commit()
        # check for active runs that are not the user's run
    potential_runs = UserRun.query.filter(UserRun.active_status == True, UserRun.user1 != current_user_id).all()
    final_runs = []
    for run in potential_runs: 
        #if the pace of the user is within 1.5 min of each other: 
        if abs(current_user_pace - run.user.mile_time)  < 1.5: 
            # if the duration is within 10 min of each other: 
            run_lon = float(run.lon_coordinates)
            run_lat = float(run.lat_coordinates)
            degree_distance = math.sqrt(((float(user_lat) - run_lat)**2) + ((float(user_lon) - run_lon)**2))
            miles_distance = degree_distance * CONSTANT_MI_DEGREE
            if miles_distance < 5: 
                final_runs.append((run, miles_distance))


    return render_template("user.html", user_id=user_id, runs=final_runs, user_name=user_name) # , javascript_object=javascript_object)

@app.route('/<int:user_id>/<string:user_name>/schedule_run', methods=['POST'])
def scheduling_run(user_id, user_name): 
    duration = request.form.get("amount")
    wait_time = request.form.get("time_amount")
    return render_template('schedule_run.html', duration=duration, wait_time=wait_time)


@app.route("/choose-run/<int:run_id>")
def choose_run(run_id):
    print "^^^^^^^^^^^^^^^^^^^^^^^^ making a match ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    asker_id = session['user_id']
    recipient = UserRun.query.get(run_id)
    recipient_id = recipient.user1
    new_match = Match(asker_id=session['user_id'], recipient_id=recipient_id, run_id=run_id, asked_at=datetime.datetime.now())
    db.session.add(new_match)
    db.session.commit()
    match_info = new_match.make_match_dictionary()
    match_info['recipient_name'] = recipient.user.user_name




# @app.route("/choose-run/<int:run_id>")
# def choose_run(self, run_id):            # get from url like /17

    return render_template("choose_run.html", match_info=match_info)
     
@app.route('/finding_match', methods=["POST"])
def finding_match(): 
    print "******************* making a user run *****************************"
    # Adding/updating a match column for the user currently in the session.
    lat = float(request.form.get('lat'))
    lon = float(request.form.get('lon'))
    duration = request.form.get("duration")
    duration = int(re.sub("[^0-9]", "", duration))
    wait_time = request.form.get("wait_time")  
    wait_time = int(re.sub("[^0-9]", "", wait_time))  
    time_end = datetime.datetime.now() + datetime.timedelta(minutes=wait_time) 

    # if a the user already has a match existing in the database, update it with the new info. 
    # if not, make a new match. That way, there will always be only one match per user in the Match table.
    existing_match = UserRun.query.filter_by(user1=session['user_id']).first()
    if not existing_match:
        new_match = UserRun(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_start=datetime.datetime.now(), time_end=time_end, duration=duration)
        db.session.add(new_match)
        db.session.commit()
    else: 
        lst_of_runs = UserRun.query.filter_by(user1=session['user_id']).all()
        # updating all of the user's UserRun requests to False if they are not the most current subimtted one.
        for run in lst_of_runs:
            if run.time_end  < datetime.datetime.now(): 
                run.active_status = False
                db.session.commit()
        new_match = UserRun(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_start=datetime.datetime.now(), time_end=time_end, duration=duration)
        db.session.add(new_match)
        db.session.commit()
        
    return "success"


@app.route('/inbox/requests/<int:user_id>')
def show_requests(user_id): 
    # the user in the session here is the person that is the recipient.
    possible_matches = Match.query.filter(Match.recipient_id == session['user_id']).all()
    jinja_content ={}
    if not possible_matches: 
        jinja_content['message'] = "no matches for now. Feel free to go to your profile and make as many matches as you would like!"
    else: 
        jinja_content['message'] = "you have %d requests to run!" % (len(possible_matches))
        jinja_content['matches'] = []
        for match in possible_matches:
            run_info = match.run 
            asker_info = User.query.get(match.asker_id)
            # we are putting a list of tuples that are the match, and run corresponding to that match that the recipeint made.
            jinja_content['matches'].append((match, run_info, asker_info))
            print "jinja_dictionary of matches", jinja_content['matches']
        jinja_content['possible_matches'] = possible_matches
    print "our jinja dictionary: ", jinja_content
    return render_template("inbox.html", jinja_content=jinja_content)


@app.route('/make_run/confirmation/<int:match_id>')
def run_confirmation(match_id): 
    # handling accpting on the match table
    accepted_match = Match.query.get(match_id)
    accepted_match.accepted = True
    asker_number = User.query.get(accepted_match.asker_id).phone
    asker_name = accepted_match.user.user_name
    recipeint_number = User.query.get(accepted_match.recipient_id).phone 
    print "asker number and recipient number: ", asker_number, recipeint_number 
    client = TwilioRestClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    message=client.messages.create(from_=os.environ['TWILLIO_NUMBER'], to=recipeint_number, body=("Hello! %s wants to go on the run you posted!") % (asker_name))
    print message.sid 
    return "success"

@app.route('/make_run/no-thanks/<int:match_id>')
def run_rejection(match_id):
    rejected_match = Match.query.get(match_id)
    rejected_match.accepted = False

    #handling rejection
    return "you have rejected"




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()