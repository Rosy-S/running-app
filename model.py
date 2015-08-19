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


class User_Run(db.Model): 
	__tablename__ = "user_runs"

	run_id = db.Column(db.Integer,autoincrement=True, primary_key=True)
	user1 = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	active_status = db.Column(db.Boolean, nullable=False, default=True)
	lat_coordinates = db.Column(db.Float, nullable=False)
	lon_coordinates = db.Column(db.Float, nullable=False)
	time_start = db.Column(db.DATETIME, default=datetime.datetime.now())
	time_end = db.Column(db.DATETIME)
	duration = db.Column(db.Integer)

	# Define relationship to user
	user = db.relationship("User",
						   backref=db.backref("user_runs", order_by=user1))

	# preferences = db.relationship("Preferences", 
	#                                 backref=db.backref("preferences", order_by=user1))

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<User_Run id for user1=%s is %s, time_start=%s>" % (self.user1, self.run_id, self.time_start)

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
	# asker is the person that is interested in going on a run on the User_Run you made. 
	asker_id = db.Column(db.Integer, db.ForeignKey('users.user_id',))
	run_id = db.Column(db.Integer, db.ForeignKey('user_runs.run_id'))
	asked_at = db.Column(db.DATETIME)
	viewed = db.Column(db.DATETIME)
	accepted = db.Column(db.Boolean)

	# defining relationship to user tale
	user = db.relationship("User",
						   backref=db.backref("user_matches", order_by=asker_id)) 

	run = db.relationship("User_Run", 
							backref=db.backref("run_matches", order_by=run_id))


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