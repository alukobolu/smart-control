from __future__ import absolute_import,unicode_literals
from smartcontrol.celery import app
from notifications.utils import send_push_message
from accounts.models import UserAccount,User
import datetime 
@app.task(name='send-notification', bind=True)
def send_notification(self,users, title, message) :
    try:
        if users == "ALL":
            user_accounts = UserAccount.objects.all()
            for user in user_accounts:
                token = user.expo_push_token
                try : 
                    send_push_message(token, title, message)
                except : 
                    pass
        else:
            emails = users.split(",")
            for email in emails:
                user = User.objects.get(email = email)
                user_account = UserAccount.objects.get(user = user)
                token = user_account.expo_push_token

                try : 
                    send_push_message(token, title, message)
                except : 
                    pass
            
        return
    except:
        pass


