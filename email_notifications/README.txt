This is an email notification python app that runs locally. It runs on the background, taking relatively little resources from your computer. 
It was built as an exercise only, not meant for distribution, and is not safe enough for that purpose. 
To make it work, you need to create an email account from which notifications will be sent (again, it's a local app, no external services envolved). 
This email address should preferably be created for this purpose only, as you provide its password in the code. Of course, your personal email (to which notifications are sent)
is NOT compromized in any way, and you do not write its password anywhere. 
The goal behind this exercise was using smtplib, and building a scheduler without using any of the scheduler libraries available. 
Written on python 3.5, not tested on earlier versions.

- pip install smtplib.
- Create an email account for sending emails. Gmail needs an additional step of allowing SMTP access (use this link: https://myaccount.google.com/lesssecureapps?pli=1)
- Complete the necessary fields at the top of the email_notifications.py code.  
- Place an empty .txt file called log_for_notifications.txt in the directory of the py code (provided in this repository). This is needed in order to log the number of iterations the code checked for events,
  for logging the number of iterations remain till the end of the script (you decide how long the code will run, it can event be months long), and for error logging. 
  Another function of this txt file is to make sure that only one instance of this code is running. This is the reason it should be empty when you lounch the code.
- Create an even list .txt file called notifications.txt (you can base yours on the one provided here). This file should have a very speicific format. See below, as well as the file provided in the repository. 
-Now you can run the code in the background. Open cmd and type: your_python_path\pythonw.exe notifications_code_path\email_notifications.py 


How to build the event txt file:

It's simple (see examples below). Write the event date and time in the format below. Do not place a zero in the tens place (e.g. eight o'clock should be written 8, and not 08. Similarly april is 4, not 04).
The message to appear in the subject of the notification email should be written on the right hand side of the '=' sign. 
Weekly events should be marked with <weekly> right after the message, and monthly events should be marked with <monthly>. 
Events that are done (email was sent) will be automatically marked as <done> be the system. You don't have to remove them though you can.
When a weekly or a monthly event is done, the system will generate a new event entry inside the txt file for the next iteration. 

2018, 4, 10, 8, 30 = a notification message here
2018, 4, 27, 9, 0 = a monthly event message here <monthly>
2018, 4, 10, 12, 15 = a weekly event message here <weekly>


-- boaz, 2018 