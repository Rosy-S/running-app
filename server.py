from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

import datetime

from model import connect_to_db, db, User, Preference, Match

import re


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "MuchSecretWow"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

# def get_user_object(): 
#     if 'user_id' in session: 
#         user_object = User.query.get(session['user_id'])
#         return user_object
#     else: 
#         print("no user in session")

# user_object = get_user_object()



@app.route('/')
def index():
    """Homepage."""

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


    new_user = User(user_name=user_name, password=password, email=email)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % user_name)

    user = new_user 
    session["user_id"] = user.user_id
    session["user_name"] = user.user_name

    return render_template("profile_details.html")

@app.route('/confirmation', methods=['POST'])
def confirmation(): 
    mile_time = request.form["mile_time"]
    gender_preference = request.form["gender_preference"]
    phone = request.form["phone"]
    user_id = session['user_id']
    user = User.query.get(user_id)

    # making preferences for a user
    preferences = Preference(user_id=user_id, phone=phone, mile_time=mile_time, gender_preference=gender_preference)
    db.session.add(preferences)
    db.session.commit()
    flash("your preferences have been updated! Thanks!")

    # updating gender for a user
    gender = request.form["gender"]
    user.gender = gender
    db.session.commit()

    return redirect("/users/%s/%s" % (user.user_id, user.user_name))

    
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


@app.route('/logout')
def logout():
    """Log out."""

#FIX-ME:  HOW TO DELETE WHOLE DITIONARIES INSTEAD OF JUST KEYS...
    del session["user_id"]
    del session['user_name']
    flash("Logged Out.")
    return redirect("/")


########USER LOGGED IN ROUTES########################

@app.route("/users/<int:user_id>/<user_name>")
def user_detail(user_id, user_name):
    """Show info about user."""

    user = User.query.get(user_id)
    user_id = int(user.user_id)
    user_name = str(user.user_name)

    return render_template("user.html", user_id=user_id, user_name=user_name)



@app.route('/<int:user_id>/<string:user_name>/schedule_run', methods=['POST'])
def scheduling_run(user_id, user_name): 
    duration = request.form.get("amount")
    wait_time = request.form.get("time_amount")
    print "duration: ", duration
    return render_template('schedule_run.html', duration=duration, wait_time=wait_time)


@app.route('/match')
def match(): 
    datetime = request.form.get("datetime")
    return render_template()


@app.route('/finding_match', methods=["POST"])
def finding_match(): 
    print "************************************************"
    # Adding/updating a match column for the user currently in the session.
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    session['lat'] = lat
    session['lon'] = lon
    print "session: ", session
    duration = request.form.get("duration")
    duration = int(re.sub("[^0-9]", "", duration))
    wait_time = request.form.get("wait_time")  
    wait_time = int(re.sub("[^0-9]", "", wait_time))  
    time_end = datetime.datetime.now() + datetime.timedelta(minutes=wait_time) 

    # if a the user already has a match existing in the database, update it with the new info. 
    # if not, make a new match. That way, there will always be only one match per user in the Match table.
    old_match = Match.query.filter_by(user1=session['user_id']).first()
    if not old_match:
        old_match = Match(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_start=datetime.datetime.now(), time_end=time_end, duration=duration)
        db.session.add(old_match)
        db.session.commit()
    else: 
        old_match.lat_coordinates = lat
        old_match.lon_coordinates = lon
        old_match.time_start = datetime.datetime.now()
        old_match.time_end = time_end
        old_match.duration = duration
        db.session.commit()

    print "new match dictionary: ", old_match.json()

    
    #Comparing the match info of the user in the current session to matches in db.
    # Need to compare their location,distance they want to run, time_end, gender preferences, and pace.
    user = User.query.get(session['user_id'])
    matches = []
    Match.query.filter_by()


    return jsonify(old_match.json())


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()