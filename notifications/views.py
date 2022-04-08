from django.shortcuts import render
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from .tasks import send_notification

#EMAIL NOTIFICATION
from django.shortcuts import render
from rest_framework.response import Response
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import  urlsafe_base64_decode
from django.utils.encoding import force_text
from accounts.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.

def SendNotifications(request: HttpRequest) -> HttpResponse:
    if request.method =="POST":
        users = request.POST['users']
        title = request.POST['title']
        message = request.POST['message']
        send_notification.apply_async(args=(users,title,message))
        return render(request, 'send_notification.html',{'success':"Successfully Sent notification"})
    elif request.method =="GET":
        return render(request, 'send_notification.html')

#EMAIL NOTIFICATION

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return ( (98) + str(timestamp)  + str(False))

account_activation_token = AccountActivationTokenGenerator()

def verify_email( account,otp, mail_subject):

    mail_subject = mail_subject
    to_email = account.email
    html_template = 'verify_email.html'

    html_message = render_to_string(html_template, {
    'name':account.firstname,'otp':otp
    })
    
    message = EmailMessage(mail_subject, html_message,  to=[to_email])
    message.content_subtype = 'html' # this is required because there is no plain text email message
    message.send()

def activate(request, uidb64, token):
    data = {}
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
        data['error'] = "Activation link is invalid!"
        return Response(data)

    if user.verified:
        data['success'] = "Your email has been verified already."
        data['verified'] = True
    else:
        if user is not None and account_activation_token.check_token(user, token):
            user.verified = True
            user.save()
            # login(request, user)
            data['success'] = "Thank you for verifying your email. Now you can login your account."
        else:
            data['error'] = "Activation link is invalid!"

    return render(request, 'index.html')

def login_email(account, mail_subject):
    mail_subject = mail_subject
    to_email = account.email
    html_template = 'login_email.html'

    html_message = render_to_string(html_template, {
    'name':account.firstname, 
    })

    message = EmailMessage(mail_subject, html_message,  to=[to_email])
    message.content_subtype = 'html' # this is required because there is no plain text email message
    message.send()

def forgot_password_email(account,otp, mail_subject):
    mail_subject = mail_subject
    to_email = account.email
    html_template = 'forgot_email.html'

    html_message = render_to_string(html_template, {
    'name':account.firstname,'otp':otp
    })

    message = EmailMessage(mail_subject, html_message,  to=[to_email])
    message.content_subtype = 'html' # this is required because there is no plain text email message
    message.send()

def welcome_email(account, mail_subject):
    mail_subject = mail_subject
    to_email = account.email
    html_template = 'welcome_email.html'

    html_message = render_to_string(html_template, {
      
        'name':account.firstname,
    })

    message = EmailMessage(mail_subject, html_message,  to=[to_email])
    message.content_subtype = 'html' # this is required because there is no plain text email message
    message.send()

def reset_successful(account, mail_subject):
    mail_subject = mail_subject
    to_email = account.email
    html_template = 'resest_password.html'

    html_message = render_to_string(html_template, {
      
        'name':account.firstname,
    })

    message = EmailMessage(mail_subject, html_message,  to=[to_email])
    message.content_subtype = 'html' # this is required because there is no plain text email message
    message.send()