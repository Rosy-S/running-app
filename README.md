# RunMate

Have you ever found yourself wanting to run, but losing motivation, wanting accountability, or just wanting someone esle to share the joy (or pain) along with you? *RunMate* is a full stack web application that helps you make that idea concrete and connect with others. Whether you feel inspired to run right now or want to schedule a time to run later,  *RunMate* takes a user's location and desired starting point, and  will find people within a 5 mile radius that also want to run and that is close to your mile time. It will notify both of the runners via text and the user's inbox when a successful match has been made. 

![Screenshot](/static/img/HomepageScreenShot.png "Homescreen")

## Table of Contents
* [Technology](#technology)
* [Using the App](#using)
* [Improvements](#improvements)

### <a name="technology"></a> Technology
*RunMate* uses the following tech stack:

* Flask - web framework
* Python - backend
* Sqlite database
* SQLAlchemy ORM
* Datetime
* Jinja2
* Regular Expressions
* JavaScript
* Jquery/Jquery UI
* Twitter Bootstrap
* HTML/CSS
* HTML5 Location
* Google Maps API
* Google Geocoding Service
* Twilio API

### <a name="using"></a> Using the App: 

#### User's Profile ####

- a user's profile shows the possible runs a user can choose and a map displying details about the run and where they are located. In order for a user to see a run, a run must be located within 5 miles of their current location (found initially at the user login), the runner has to be within a 2 min/mile difference than the user currently logged in, the run cannot be the user's own posted run, and the runs have to be active (not expired). 

![Screenshot](/static/img/Userprofile.png "User's profile")

#### Choosing a Run ####

- The map will have details of the run that will disply if you click on the runner icon. There are two types of runs you can choose: The runs that state "run now" are runs where the creator of the run wants to run right now and are open for an invitation to run. Runs that are scheduled runs are by contrast have the date and time that the run is scheduled forOn the map, they will be displayed as such, respectively:

<img src=/static/img/runningnow.png height=166 />
<img src=/static/img/Scheduledrun.png height=166 />

- Once a user clicks on "Choose this run" for any run, they will get a confirmation message, and it will send a text to the creator of the run that they have a match and to check their inbox.

#### Making a Run ####

- If a user does not see a run that they like or no runs are displayed, they can always make their own run. They can either click on "run now" which has a duration and a waiting time that they are willing to wait, or "schedule a run" where a user can choose the date and the time that they want to run. They will be displayed as such, respectively:

<img src=/static/img/MakingNowRun.png height=240 />
<img src=/static/img/MakingScheduledRun.png height=240 />

- After they enter their details for either "run now" or "schedule a run," they will be taken to the following window to choose their start location. The default start location is their location at the current time: 

![Image](/static/img/MarkingLocation.png "Marking location")

- Once they have finished, the user will get a confirmation on the screen signaling that the run has been created and is open.

#### Accepting or Denying a Run ####

- Once a user gets a text that they have a match, they can check their inbox to accept or decline. Accepting a match sends a confirmation text message to the other user and deactivates the run, since the user has already found a match. Declining a match deletes the match from the match table (the run still stays active)

![Image](/static/img/inbox.png "inbox")

### <a name="improvements"></a> Improvements: 

Websockets - In the future, I would like to be able to implement websockets so that as soon as a run that you have made gets a match, you will be able to accept while you are still on the website and not have to wait to accept by an inbox. This is useful especially for the users that choose the "run now" time frame

Test Coverage - Write integration, unit, and doctests throughout the code in order to refactor and implement more features with the assurance that the functionallity of the app will not change. 

Tracking of past runs - I would like to add another table to the database of past runs so that users will be able to document when they ran and who they ran with, as well as tracking information to see if their mile time has improved. 

Seperating "run now" and scheduled runs - Right now, all possible runs are listed in the same place. I would liketo seperate the runs so that the "run now" runs that are expiring soon are displayed at the top, and the scheduled runs are ordered based on when their start date is. 

Re-ocurring runs - The app accounts for users that want to run now or that want to schedule a run, but it would also be cool if users can schedule re-occuring runs (i.e. if a user usually runs on Saturdays at 11:00 AM, the user can specify that and the web app will automatically make the run)

