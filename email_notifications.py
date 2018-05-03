# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 21:06:41 2018

@author: boaz sadeh
"""

import smtplib
from datetime import datetime
from datetime import timedelta
import time
import re
import traceback


##
sender = "myAutoPyEmail@gmail.com" 
psw = "d#NWeb2@R"
dst_email = "boaz@elminda.com"
event_file = r"C:\Users\lab28\Dropbox\py\MyPy\exercises\notifications.txt"
log_fle = r"C:\Users\lab28\Dropbox\py\MyPy\exercises\log_for_notifications.txt"
iters_to_run = 60*24*7 # iterations 
##

class SendEmail(object):
    def __init__(self, sender, psw, dst_email, event_file):
        self.sender = sender
        self.psw = psw
        self.recipient = dst_email
        self.event_file = event_file
        
    def _set_tasks(self):
        self.tasks = []
        self.messages = []
        self.jobs = WritableDict(self.event_file)
        for key, val in self.jobs.items():
            hands = [int(i) for i in key.split(sep=',')]
            self.tasks.append(datetime(hands[0], hands[1], hands[2], hands[3], hands[4]))
            self.messages.append(val) 
    
    def _get_message(self, message):  
        if re.search('<done>',message):
            flag = 0
        elif re.search('<monthly>',message):
            message = "Monthly reminder: {}".format(re.split("<monthly>", message)[0])
            flag = 3
        elif re.search('<weekly>',message):
            message = "Weekly reminder: {}".format(re.split("<weekly>", message)[0])
            flag = 2
        else:
            message = "Reminder: {}".format(message)
            flag = 1
#        message = "Subject: {}\n\n{}".format(subject, text)
        return message, flag
        
    def _send_email(self, message):
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(self.sender, self.psw)
        smtp_server.sendmail(self.sender, self.recipient, "Subject: {}".format(message))
        smtp_server.close()
        
    def _update_task_list(self, task, message, flag):
        key = []
        newmessage = []
        key.append(str(task.year) + ', ' + str(task.month) + ', ' + str(task.day)
                      + ', ' + str(task.hour) + ', ' + str(task.minute) + ' ')
        if flag == 0:
            newmessage.append(message)
        else:
            newmessage.append(message + ' <done>')
        if flag == 2:
            newtask = task+timedelta(days = 7)
            key.append(str(newtask.year) + ', ' + str(newtask.month) + ', ' + str(newtask.day)
                      + ', ' + str(newtask.hour) + ', ' + str(newtask.minute) + ' ')
            newmessage.append(message)
        elif flag == 3:
            if task.month != 12:
                key.append(str(task.year) + ', ' + str(task.month+1) + ', ' + str(task.day)
                              + ', ' + str(task.hour) + ', ' + str(task.minute) + ' ')
            else:
                key.append(str(task.year+1) + ', ' + '1' + ', ' + str(task.day)
                          + ', ' + str(task.hour) + ', ' + str(task.minute) + ' ')
            newmessage.append(message)
        return key, newmessage
            
    def check_now(self):
        self._set_tasks()
        for t in range(0,len(self.tasks)):
            task = self.tasks[t]
            delta = datetime.today() - task
            if delta.days == 0 and delta.seconds < 62:
                message, flag = self._get_message(self.messages[t])
                if not re.search("<done>", message):
                    self._send_email(message)
                    message = message + ' <done>'
                keys, newmessages = self._update_task_list(self.tasks[t], self.messages[t], flag)
                for i, j in zip(keys, newmessages):
                    self.jobs[i] = j
#                self._set_tasks()                            
            
class WritableDict(dict):
    
    def __init__(self, filename):    
        self.filename = filename
        with open(self.filename, 'r') as fn:
            self.contents = fn.readlines()
            for line in self.contents:
                key, value = self._validate(line)            
                dict.__setitem__(self,key,value)
                
    def _validate(self,line):
        if not re.search("=", line):
            raise TypeError("a '=' sign is missing in: {}".format(line)) 
        key = line.split('=')[0]
        value = line.split('=',1)[1].strip()
        try:
            [int(i) for i in key.split(sep=',')]
        except:
            raise ValueError("date is not in an integer-only format in: {}".format(key))
        return key, value                
            
    def __setitem__(self, key, value): 
        dict.__setitem__(self,key,value)       
        with open(self.filename, 'w') as fn:
             for key, val in self.items():
                 str2write = '{0}={1}\n'.format(key,val)     
                 fn.write(str2write)



logobj = WritableDict(log_fle)
if logobj:
    logobj["error"] = "log file is not empty, another instance of this code may be running now"
    exit(False)
    
mailingjobs = SendEmail(sender, psw, dst_email, event_file)

for cnt in range(1,iters_to_run+1):
    try:
        mailingjobs.check_now()
    except:
        cnt = iters_to_run
        message = traceback.format_exc()
        logobj["error"] = message
        exit(False)
    else:
        logobj["Notification iterations made "] = cnt
        logobj["Left to run "] = iters_to_run-cnt
        time.sleep(60)
logobj["Script finished. Number of iterations made "] = cnt