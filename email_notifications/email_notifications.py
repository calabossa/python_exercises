# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 21:06:41 2018

@author: boaz sadeh
"""

import smtplib
import imaplib
from datetime import datetime
from datetime import timedelta
import time
import re
import traceback
import os


##
sender = "email@domain.com" # From here notifications will be sebt
psw = os.environ.get('MY_PY_MAIL_PSWD')
dst_email = "myPersonalEmail@domain.com" 
event_file = r"C:\Users\...\notifications.txt"
log_fle = r"C:\Users\...\log_for_notifications.txt"
days_to_run = 30 # iteration every nimute for the specified numb of days
summary_day = 6 # 0: monday, 1: tuesday, 2: wednesday, 3: thursday, 4: friday, 5: saturday, 6: sunday
summary_hour = 7
##


iters_to_run = round(days_to_run*24*60)

class SendEmail(object):
    def __init__(self, sender, psw, dst_email, event_file):
        self.sender = sender
        self.psw = psw
        self.recipient = dst_email
        self.event_file = event_file
        
    def _set_tasks(self, tasks_from_email):
        self.tasks = []
        self.messages = []
        self.jobs = WritableDict(self.event_file)
        if tasks_from_email:
            self._update_from_email()
        for key, val in self.jobs.items():
            hands = [int(i) for i in key.split(sep=',')]
            self.tasks.append(datetime(hands[0], hands[1], hands[2], hands[3], hands[4]))
            self.messages.append(val) 
    
    def _get_message(self, message):  
        if re.search('<done>',message):
            flag = 0
        elif re.search('<yearly>',message):
            message = "Yearly reminder: {}".format(re.split("<yearly>", message)[0])
            flag = 4
        elif re.search('<monthly>',message):
            message = "Monthly reminder: {}".format(re.split("<monthly>", message)[0])
            flag = 3
        elif re.search('<weekly>',message):
            message = "Weekly reminder: {}".format(re.split("<weekly>", message)[0])
            flag = 2
        elif re.search('<daily>',message):
            message = "daily reminder: {}".format(re.split("<daily>", message)[0])
            flag = 5
        elif re.search('<daily no weekends>',message):
            message = "daily reminder: {}".format(re.split("<daily no weekends>", message)[0])
            flag = 6
        else:
            message = "Reminder: {}".format(message)
            flag = 1
#        message = "Subject: {}\n\n{}".format(subject, text)
        return message, flag
        
    def _send_email(self, message, summary_mail = False):
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(self.sender, self.psw)
        if not summary_mail:
            sepr = message.find('|')
            if sepr != -1:
                message = message[0:sepr] + '\n\n' + message[sepr+1:]
            smtp_server.sendmail(self.sender, self.recipient, "Subject: {}".format(message))
        else: 
            smtp_server.sendmail(self.sender, self.recipient, message)
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
        if flag == 4:
            key.append(str(task.year+1) + ', ' + str(task.month) + ', ' + str(task.day)
                              + ', ' + str(task.hour) + ', ' + str(task.minute) + ' ')
            newmessage.append(message)
        if flag == 5:
            newtask = task+timedelta(days = 1)
            key.append(str(newtask.year) + ', ' + str(newtask.month) + ', ' + str(newtask.day)
                      + ', ' + str(newtask.hour) + ', ' + str(newtask.minute) + ' ')
            newmessage.append(message)
        if flag == 6:
            dayname = task.strftime("%A")
            if dayname == "Thursday":
                newtask = task+timedelta(days = 3)
            elif dayname == "Friday":
                newtask = task+timedelta(days = 2)
            else:
                newtask = task+timedelta(days = 1)
            key.append(str(newtask.year) + ', ' + str(newtask.month) + ', ' + str(newtask.day)
                      + ', ' + str(newtask.hour) + ', ' + str(newtask.minute) + ' ')
            newmessage.append(message)
        return key, newmessage
    
    def _update_from_email(self):
#        self.jobs["2018, 11, 11, 11, 11"] = "TEST"
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.sender, self.psw)
            mail.select("inbox") # connect to inbox.
            new = mail.search(None, "unseen")[1][0]
            if new:
                newb = [a.encode() for a in new.decode().split(' ')]
                mcnt = len(newb)-1
                while mcnt > -1:   
                    nb = newb[mcnt]
                    result, data = mail.fetch(nb, "(RFC822)")
                    raw_email = data[0][1] 
                    contents = raw_email.decode()
                    st = contents.find('>>>')+3
                    en = contents.find('<<<')   
                    if en != -1:
                        emessage = contents[st:en]
                        eq = emessage.find('=')
                        self.jobs[emessage[0:eq]] = emessage[eq+1:]
                    mcnt -= 1
            mail.close()
            mail.logout() 
        except:
            pass    
 
    def _send_summary_email(self):
        keys = list(self.jobs.keys())
        keys = sorted(keys)
        keylist = []
        dltas = []
        for j in keys:
            d = [int(i) for i in j.split(',')]
            d[-2]=23
            d[-1]=59
            keylist.append(d)
            dltas.append(datetime(*map(int, d)) - datetime.now())
        inds = [i for i in range(0,len(dltas)) if dltas[i].days>=0]
        subject = "Future Event Summary"
        text = ''
        cnt = 0
        for i in inds:
            cnt += 1
            when = datetime(*map(int,keys[i].split(',')))
            wd = when.weekday()
            day = days.get(wd)
            dif = dltas[i] # when - datetime.now()
            dif = dif.days
            text += "#{}:  {}, {} (in {} days): {}".format(cnt, day, keys[i], 
                      dif, self.jobs[keys[i]]) + "\n\n" 
        curr_message = "Subject: {}\n\n{}".format(subject, text)
        self._send_email(curr_message, summary_mail = True)
        
    def _send_warning_email(self):
        subject = "email-reminder run is about to end"
        text = "This is an automated message to remind you that the python email"\
                " reminder application will finish the required run period in 24 hours"\
                " from now.\nIf you are interested in continuing the task, please re-run the script"\
                " or log out and in to your computer."
        curr_message = "{}\n\n{}".format(subject, text)
        self._send_email(curr_message)
           
    def check_now(self, tasks_from_email = False):
        self._set_tasks(tasks_from_email)
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
 

with open(log_fle, 'w') as fn: 
    fn.write('')
    
logobj = WritableDict(log_fle)
#if logobj:
#    logobj["error"] = "log file is not empty, another instance of this code may be running now"
#    exit(False)
    
mailingjobs = SendEmail(sender, psw, dst_email, event_file)
start = str(datetime.now())
summary_flag = 0
warning_flag = True
days={}
days[0] = 'Monday'
days[1] = 'Tuesday'
days[2] = 'Wednesday'
days[3] = 'Thursday'
days[4] = 'Friday'
days[5] = 'Saturday'
days[6] = 'Sunday'

for cnt in range(1,iters_to_run+1):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if cnt %30 == 0:
            mailingjobs.check_now(tasks_from_email = True)
        else:
            mailingjobs.check_now()
            
        today = datetime.now().weekday()
        tohour = datetime.now().hour 
        if summary_day - today == 1:
            summary_flag = 0 
        if summary_day - today == 0:
            if tohour - summary_hour > 0 and summary_flag == 0:
                summary_flag = 1
                mailingjobs._send_summary_email()
        if days_to_run > 1 and iters_to_run-cnt < 1440 and warning_flag: 
            mailingjobs._send_warning_email()
            warning_flag = False

    except:
        cnt = iters_to_run
        message = traceback.format_exc()
        logobj["ERROR occured at "] = now
        logobj["error"] = message
        exit(False)
    else:
        logobj["script started on "] = start + ";   cheking once per minute." 
        logobj["Notification iterations made "] = cnt
        logobj["last check for notification "] = now
        logobj["Left to run "] = iters_to_run-cnt
        time.sleep(60)
logobj["Script finished. Number of iterations made "] = cnt



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
