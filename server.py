from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from datetime import datetime

from model import connect_to_db, db, User, Preference, Match


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "MuchSecretWow"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined




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

    flash("Logged in")
    return redirect("/users/%s/%s" % (user.user_id, user.user_name))


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")



@app.route("/users/<int:user_id>/<user_name>")
def user_detail(user_id, user_name):
    """Show info about user."""

    user = User.query.get(user_id)
    return render_template("user.html", user=user)

@app.route('/schedule_run')
def scheduling_run(): 
	return render_template('schedule_run.html')
	# return render_template('test.html')
# GET http://localhost:5000/favicon.ico 404

@app.route('/finding_match')
def finding_match(): 
    print "************************************************"
    print "session id: ", session['user_id']
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    duration = request.form.get("datetime")
    print "lat = ", lat
    print "lon = ", lon
    print "datetime: ", datetime

    a = datetime(2015, 8, 9, 20, 4, 49, 757635)
    new_match = Match(user1=session['user_id'], lat_coordinates=lat, lon_coordinates=lon, time_end=a, duration=30)
    db.session.add(new_match)
    db.session.commit()
    return jsonfiy(new_match.json())

        #query for matches. 

        # for each match, call match.json()

        # it will return a dictionary of attibutes


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()