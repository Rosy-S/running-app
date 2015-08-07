"""Models and database functions for Runing project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)

    # Optional info

    # if gender = True, user is female. if 
    gender = db.Column(db.String(6), nullable=True)
    # Everything else besides user_name and password is nullable. User only needs those two
    # things to login and make a profile. If they don't specify mile_time, they don't care who
    # they get paird with or don't know their miletime. If they don't provide their phone, 
    # then they don't want to be texted. They can still use the website for pinning.


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_name=%s email=%s>" % (self.user_name, self.email)
class Preference(db.Model): 
    __tablename__ = 'preferences'

    preference_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    #Optional contact info
    phone = db.Column(db.Integer, nullable=True)
    #Pairing Info
    mile_time = db.Column(db.Integer, nullable=True)
    #if True, user is a Female. If False, user is a Male, if blank, user doesn't 
    # care on who they get paired with or don't want to specify.
    gender_preference = db.Column(db.String(3), nullable=True)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("preferences", order_by=user_id))
    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s>" % (self.user_id)


class Match(db.Model): 
    __tablename__ = "matches"

    match_id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    user1 = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    active_status = db.Column(db.Boolean, nullable=False, default=True)
    lat_coordinates = db.Column(db.Integer, nullable=False)
    lon_coordinates = db.Column(db.Integer, nullable=False)
    time_start = db.Column(db.DATETIME, default=datetime.now())
    time_end = db.Column(db.DATETIME)
    duration = db.Column(db.Integer)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("matches", order_by=user1))
    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Match for user1=%s, time_start=%s>" % (self.user1, self.time_start)

    def json(self):
        my_json_representation = {}
        my_json_representation['user'] = self.user
        my_json_representation['active_status'] = self.active_status
        my_json_representation['lat_coordinates'] = self.lat_coordinates
        my_json_representation['lon_coordinates'] = self.lon_coordinates
        my_json_representation['time_start'] = self.time_start
        my_json_representation['time_end'] = self.time_end
        my_json_representation['duration'] = self.duration

        # finish adding all the atributes to this json thingie
        return my_json_representation

# class Run(db.Model): 
#     __tablename__ = "runs"

#     pass



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///runapp.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."