from html import entities
from django.shortcuts import render
import os.path
import requests
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

cloud_project_id = 'smartcontrol-346211'
SCOPES = ['https://www.googleapis.com/auth/androidmanagement']
DOCUMENT_ID = '195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE'

def first(request):
    return render(request,'index.html')

def main(request):
    if os.path.exists('client_secret_340732573184-hq4857tc435tb1mriahj6ggknlr499ag.apps.googleusercontent.com.json.json'):
        print("hey")
        # smartcontrol-346211-47d33cd1b55f.json
        creds = Credentials.from_authorized_user_file('client_secret_340732573184-hq4857tc435tb1mriahj6ggknlr499ag.apps.googleusercontent.com.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_340732573184-hq4857tc435tb1mriahj6ggknlr499ag.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        print('The title of the document is: {}'.format(document.get('title')))
        return render(request,'index.html',{'info': document.get('title')})
    except HttpError as err:
        print(err)

def SignupUrls(request):
    headers = {
        "Content-Type": "application/json",
    }
    url = "https://androidmanagement.googleapis.com/v1/signupUrls"
    data1={
        "projectId": f"{cloud_project_id}",  
        "callbackUrl": "https://smartcontrolapp.herokuapp.com/callback", 
    }
    data2 = json.dumps(data1 , indent=4)
    response = requests.post(url=url , headers=headers , data=data2)
    print(response)
    print(response.json())
    return render(request,'index.html')

def CallBack(request):
    enterpriseToken = request.get('enterpriseToken')
    print(enterpriseToken)
    return render(request,'index.html')