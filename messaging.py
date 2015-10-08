from twilio.rest import TwilioRestClient
from twilio import twiml
import os

client = TwilioRestClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

def choosing_run(recipient_number, asker_name, match_id): 
	message=client.messages.create(from_=os.environ['TWILLIO_NUMBER'], to=recipient_number, body=("Hey there! %s wants to go on the run you posted! Go to your inbox, or text back the number '%d' followed by either 'Yes' or 'No' to confirm.") % (asker_name, match_id))

def confirmation_text(asker_number, recipient_name, time_start): 
	message=client.messages.create(from_=os.environ['TWILLIO_NUMBER'], to=asker_number, body=("Hello! %s got the message that you want to run with them! You are running with them on %s!") % (recipient_name, time_start))

