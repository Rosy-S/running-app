from jinja2 import StrictUndefined
from twilio import twiml
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, UserRun

import datetime
import re, math

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

    print "our session dictionary: ", session

    

    flash("Logged in")
    return redirect("/users/%s/%s" % (user.user_id, user.user_name))

@app.route('/meta-login', methods=['POST'])
def function(): 
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    session['lat']  = lat
    session['lon'] = lon 
    print lat, lon 
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
            print "run_lon: ", run_lon
            print "run_lat: ", run_lat
            degree_distance = math.sqrt(((float(user_lat) - run_lat)**2) + ((float(user_lon) - run_lon)**2))
            miles_distance = degree_distance * CONSTANT_MI_DEGREE
            print "miles distance: ", miles_distance
            if miles_distance < 5: 
                final_runs.append((run, miles_distance))
    # print "final_runs: ", final_runs
    # # if matches are empty, skip the whole twilio thing, and go to a page. 
    # #else, pick a match from matches. and send a twilio message, adn then go to the same webpage. 

    # runs_to_return = {}
    # if not final_runs: 
    #     print "NO current runs.... "
    #     javascript_object = {}

    # else:
    #     # in this step, we have the list of final runs that are not expired, and that need to show up on the user page.
    #     # right now they are objects, so we are trying to convert them to json objects that will render in the page and that
    #     # can be manipulated with JS. 
    #     print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&" 
    #     for run, distance in final_runs: 
    #         print "RUN: ", run
    #         print "Distance: ", distance
    #         run_dictionary = run.json()
    #         # getting match user's pace and name and adding it to match_dictionary
    #         run_dictionary['pace'] = run.user.mile_time
    #         run_dictionary['user name'] = run.user.user_name
    #         run_dictionary['distance_away'] = distance

    #         print "our run_dictionary: ", run_dictionary


    #         if runs_to_return == {}:            
    #             runs_to_return['match']= [run_dictionary]
    #             print "Im in the if"
    #         else: 
    #             runs_to_return['match'].append(run_dictionary)
    #             print "Im in the else"
    #         print "runs_to_return: ", runs_to_return
    #         print "runs_to_return length : ", len(runs_to_return)


    #         # print "our final matches: " + str(run) + "\n"
    #         # print "Our json version: " + str(run_dictionary) + "\n"

    #         javascript_object = runs_to_return

    #         print "our javascript objert: ", javascript_object


    # I want to display the list of all possible runs that this user can go on. 
    # check that list to see if there is any expired runs, and don't display the ones iwth active status = False
    # how would I do that? I have their user

    return render_template("user.html", user_id=user_id, runs=final_runs, user_name=user_name) # , javascript_object=javascript_object)

@app.route('/<int:user_id>/<string:user_name>/schedule_run', methods=['POST'])
def scheduling_run(user_id, user_name): 
    duration = request.form.get("amount")
    wait_time = request.form.get("time_amount")
    return render_template('schedule_run.html', duration=duration, wait_time=wait_time)


@app.route("/choose-run/<int:run_id>")
def choose_run(run_id):
    asker_id = session['user_id']
    recipient = UserRun.query.get(run_id).user1
    match = Match(asker_id=session['user_id'], recipient_id=recipient_id, run_id=run_id, asked_at=datetime.datetime.now())
    db.session.add(match)
    db.session.commit()
    


# @app.route("/choose-run/<int:run_id>")
# def choose_run(self, run_id):            # get from url like /17

    return render_template("choose_run.html")
     
@app.route('/finding_match', methods=["POST"])
def finding_match(): 
    print "************************************************"
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
            print "active status of match: ", run.active_status
        new_match = UserRun(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_start=datetime.datetime.now(), time_end=time_end, duration=duration)
        db.session.add(new_match)
        db.session.commit()
        

#         old_match.lat_coordinates = lat
#         old_match.lon_coordinates = lon
#         old_match.time_start = datetime.datetime.now()
#         old_match.time_end = time_end
#         old_match.duration = duration
#         db.session.commit()

#     # print "new match dictionary: ", old_match.json()

    
#     #Comparing the match info of the user in the current session to matches in db.
#     # Need to compare their gender preferences, pace, duration, time_end, and location.
#     current_user = User.query.get(session['user_id'])
#     current_user_pace = (current_user.mile_time)
#     current_user_duration = duration
#     current_user_end_time = time_end
#     #querying first for all UNEXPIRED possible matches that are not the user itself.
#     potential_runs = UserRun.query.filter(UserRun.time_end > datetime.datetime.now(), UserRun.user1 != current_user.user_id).all()

#     #querying for pace, duration, and location
#     runs = []
#     for run in potential_runs: 
#         run_preferences = run.user.mile_time
#         #if the pace of the user is within 1.5 min of each other: 
#         if abs(current_user_pace - run.user.mile_time)  < 1.5: 
#             # if the duration is within 10 min of each other: 
#             if abs(current_user_duration - run.duration) < 15:
#                 # if the location is within a 3 mile radius of one another:
#                 run_lon = float(run.lon_coordinates)
#                 run_lat = float(run.lat_coordinates)
#                 degree_distance = math.sqrt(((lat - run_lat)**2) + ((lon - run_lon)**2))
#                 miles_distance = degree_distance * CONSTANT_MI_DEGREE
#                 print "miles distance: ", miles_distance
#                 if miles_distance < 5: 
#                     runs.append(run)
#     # if matches are empty, skip the whole twilio thing, and go to a page. 
#     #else, pick a match from matches. and send a twilio message, adn then go to the same webpage. 

#     runs_to_return = {}
#     for run in runs: 
#         run_dictionary = run.json()
#         # getting match user's pace and name and adding it to match_dictionary
#         run_dictionary['pace'] = run.user.mile_time
#         run_dictionary['user name'] = run.user.user_name
#         if runs_to_return == {}:            
#             runs_to_return['match']= [run_dictionary]
#         else: 
#             runs_to_return['match'].append(run_dictionary)

#         print "our final matches: " + str(run) + "\n"
#         print "Our json version: " + str(run_dictionary) + "\n"

# # for each match return the jsonified form....
# # FIX ME: rename the match.format_json()
#     return jsonify(runs_to_return)
    return "success"


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()