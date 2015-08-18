from twilio.rest import TwilioRestClient
import os

client = TwilioRestClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

# this is the command to send a text number from your twillio number to the to number with the message of body.
message=client.messages.create(from_=os.environ['TWILLIO_NUMBER'], to=os.environ['to_number'], body="Hello! This is rosy, this is myself")

# when it sends a message, it will make a unique id. This is going to tell you if it did something or not.
print message.sid 