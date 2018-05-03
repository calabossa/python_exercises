This is an email notification python app that runs locally. It runs on the background, taking relatively little resources from your computer. 
It was built as an exercise only, not meant for distribution, and is not safe enough for that pirpose. 
To make it work, you need to create an email account from which notifications will be sent (again, it's a local app, no external services envolved). 
This email address should preferably be created for this purpose only, as you provide its pass in the code. Of course, your personal email (to which notifications are sent)
is NOT compromized in any way, and you do not write its pass anywhere. 
The goal behind this exercise was using smtplib, and building a scheduler without any of the schedule libraries available. 
Written on python 3.5, not tested in earlier versions.

- pip install smtplib.
- Create an email account for sending emails. Gmail needs an additional step of alowing SMTP access (use this link: https://myaccount.google.com/lesssecureapps?pli=1)
- Complete the necessary fields at the top of the email_notifications.py code.  
- Place an empty txt file called log_for_notifications.txt in the directory of the py code. This is needed in order to log the number of iterations the code checked for events,
  for logging the number of iterations remains till the end of the script (you decide how long the code will run, it can be months), and for error logging. 
  Another function of this txt file is to make sure that only one instance of this code is running. This is the reason it should be empty when you lounch the code.
- Create an even list txt file called notifications.txt. This file should have a very speicific format. See below, as well as an example in the repository. 
-Now you can run the code in the background. Open cmd and type: your_python_path\pythonw.exe notifications_code_path\email_notifications.py 


-- boaz, 2018 