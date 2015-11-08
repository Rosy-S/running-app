from model import User, UserRun, Match, connect_to_db, db
from server import app
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

def load_users():
    """Load users from user.csv into database."""

    lines = [line.rstrip('\n') for line in open("seed_data/users.csv")]

    for line in lines: 
        column_data = line.split(",")
        line = User(user_id=column_data[0], user_name=column_data[1], password=column_data[2], email=column_data[3], phone=column_data[4], mile_time=column_data[5])
        db.session.add(line)
    db.session.commit()


def load_userRuns(): 
    """Load user runs from user_runs into database."""
    lines = [line.rstrip('\n') for line in open("seed_data/user_runs.csv")]    
    for line in lines: 
        column_data = line.split(",")
        line = UserRun(run_id=column_data[0], user1=column_data[1], active_status=column_data[2], lat_coordinates=column_data[3], lon_coordinates=column_data[4], scheduled=column_data[5])
        db.session.add(line)
    db.session.commit()

def load_matches(): 
    """Load matches from matches.csv into database."""
    lines = [line.rstrip('\n') for line in open("seed_data/matches.csv")]    
    for line in lines: 
        column_data = line.split(",")
        line = Match(match_id=column_data[0], asker_id=column_data[1], recipient_id=column_data[2], run_id=column_data[3], asked_at=column_data[4], viewed=column_data[5], accepted=column_data[6])
        db.session.add(line)
    db.session.commit()

if __name__ == "__main__": 
	connect_to_db(app)

	load_users()
	load_userRuns()
	load_matches()
