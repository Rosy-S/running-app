"""Models and database functions for Runing project."""

from flask_sqlalchemy import SQLAlchemy
import datetime

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
	phone = db.Column(db.Integer, nullable=True)
	mile_time = db.Column(db.Integer, nullable=True)



	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<User user_name=%s email=%s>" % (self.user_name, self.email)


class UserRun(db.Model): 
	__tablename__ = "user_runs"

	run_id = db.Column(db.Integer,autoincrement=True, primary_key=True)
	user1 = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	active_status = db.Column(db.Boolean, nullable=False, default=True)
	lat_coordinates = db.Column(db.Float, nullable=False)
	lon_coordinates = db.Column(db.Float, nullable=False)
	scheduled = db.Column(db.Boolean, default=False)
	#time_start can be two things. it can be the start time for the runs happening instantaneously, 
	# and it can be the time the run was created for the runs that are going to be sheduled.
	time_start = db.Column(db.DATETIME, nullable=False)
	# scheduled_time = db.Column(db.DATETIME)
	time_end = db.Column(db.DATETIME, nullable=False)
	duration = db.Column(db.Integer)

	# Define relationship to user
	user = db.relationship("User",
						   backref=db.backref("user_runs", order_by=user1))

	# preferences = db.relationship("Preferences", 
	#                                 backref=db.backref("preferences", order_by=user1))

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<User Run id for user1=%s is %s, time_start=%s>" % (self.user1, self.run_id, self.time_start)

	def json(self):
		my_json_representation = {}
		my_json_representation['user'] = self.user1
		my_json_representation['active_status'] = self.active_status
		my_json_representation['lat_coordinates'] = self.lat_coordinates
		my_json_representation['lon_coordinates'] = self.lon_coordinates
		my_json_representation['time_start'] = self.time_start
		my_json_representation['time_end'] = self.time_end
		my_json_representation['duration'] = self.duration

		# finish adding all the atributes to this json thingie
		return my_json_representation

class Match(db.Model): 
	__tablename__ = "matches"
	
	match_id = db.Column(db.Integer,autoincrement=True, primary_key=True)
	# asker is the person that is interested in going on a run on the UserRun you made. 
	asker_id = db.Column(db.Integer, db.ForeignKey('users.user_id',))
	# recipient is the person who made the Run, that is reciving the message "asker_id wants to run with you!"
	recipient_id = db.Column(db.Integer)
	run_id = db.Column(db.Integer, db.ForeignKey('user_runs.run_id'))
	asked_at = db.Column(db.DATETIME, default=datetime.datetime.now(), nullable=False)
	viewed = db.Column(db.DATETIME)
	accepted = db.Column(db.Boolean)

	# defining relationship to user tale
	user = db.relationship("User",
						   backref=db.backref("user_matches", order_by=asker_id)) 

	run = db.relationship("UserRun", 
							backref=db.backref("run_matches", order_by=run_id))

	def make_match_dictionary(self): 
		match_dictionary = {}
		match_dictionary['match_id'] = self.match_id
		match_dictionary['asker_id'] = self.asker_id
		match_dictionary['recipient_id'] = self.recipient_id
		match_dictionary['run_id'] = self.run_id
		match_dictionary['asked_at'] = self.asked_at
		match_dictionary['accepted'] = self.accepted

		return match_dictionary 


	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<Match id%s asked by%s, run_id=%s>" % (self.match_id, self.asker_id, self.run_id)

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