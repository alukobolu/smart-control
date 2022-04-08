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

def first(request):
    return render(request,'index.html')

def authenticate(request):
    # This is a public OAuth config, you can use it to run this guide but please use
    # different credentials when building your own solution. 
    # CLIENT_CONFIG = {
    #     'installed': {
    #         'client_id':'882252295571-uvkkfelq073vq73bbq9cmr0rn8bt80ee.apps.googleusercontent.com',
    #         'client_secret': 'S2QcoBe0jxNLUoqnpeksCLxI',
    #         'auth_uri':'https://accounts.google.com/o/oauth2/auth',
    #         'token_uri':'https://accounts.google.com/o/oauth2/token'
    #     }
    # }
    # SCOPES = ['https://www.googleapis.com/auth/androidmanagement']

    # # Run the OAuth flow.
    # flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    # credentials = flow.run_console()

    # Create the API client.
    androidmanagement = build('drive', 'v3', static_discovery=False, developerKey='47d33cd1b55fa31fd02eb2b4685ae5cd72d80348')

    print('\nAuthentication succeeded.')
    return render(request,'index.html',{'info': androidmanagement})
    # return androidmanagement

def create_enterprise(androidmanagement):
    CALLBACK_URL = 'https://storage.googleapis.com/android-management-quick-start/enterprise_signup_callback.html'

    # Generate a signup URL where the enterprise admin can signup with a Gmail
    # account.
    signup_url = androidmanagement.signupUrls().create(
        projectId=cloud_project_id,
        callbackUrl=CALLBACK_URL
    ).execute()

    print('Please visit this URL to create an enterprise:', signup_url['url'])

    enterprise_token = input('Enter the code: ')

    # Complete the creation of the enterprise and retrieve the enterprise name.
    enterprise = androidmanagement.enterprises().create(
        projectId=cloud_project_id,
        signupUrlName=signup_url['name'],
        enterpriseToken=enterprise_token,
        body={}
    ).execute()

    enterprise_name = enterprise['name']

    print('\nYour enterprise name is', enterprise_name)
    enterprise_name = 'enterprises/LC00l3186x'
    return enterprise_name

def create_policy(androidmanagement,enterprise_name):
    import json
    enterprise_name = 'enterprises/LC00l3186x'
    policy_name = enterprise_name + '/policies/policy1'

    policy_json = '''
    {
    "applications": [
        {
        "packageName": "com.google.samples.apps.iosched",
        "installType": "FORCE_INSTALLED"
        }
    ],
    "debuggingFeaturesAllowed": true
    }
    '''

    androidmanagement.enterprises().policies().patch(
        name=policy_name,
        body=json.loads(policy_json)
    ).execute()
    return policy_name

    #     {'applications': [{'installType': 'FORCE_INSTALLED',
    #    'packageName': 'com.google.samples.apps.iosched'}],
    #  'debuggingFeaturesAllowed': True,
    #  'name': 'enterprises/LC00l3186x/policies/policy1',
    #  'version': '1'}

def create_entroll_token(androidmanagement,policy_name,enterprise_name):
    enrollment_token = androidmanagement.enterprises().enrollmentTokens().create(
    parent=enterprise_name,
    body={"policyName": policy_name}).execute()



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/androidmanagement']

# The ID of a sample document.
DOCUMENT_ID = '195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE'


def main(request):
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('jsons.json'):
        print("hey")
        creds = Credentials.from_authorized_user_file('smartcontrol-346211-47d33cd1b55f.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_340732573184-hq4857tc435tb1mriahj6ggknlr499ag.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        print('The title of the document is: {}'.format(document.get('title')))
        return render(request,'index.html',{'info': document.get('title')})
    except HttpError as err:
        print(err)


# if __name__ == '__main__':
#     main()

def getkey(request):
    headers = {
        "Content-Type": "application/json",
    }
    url= " https://iam.googleapis.com/v1/projects/smartcontrol-346211/serviceAccounts/Bolu@smartcontrol-346211.iam.gserviceaccount.com/keys"
    response = requests.post(url=url , headers=headers)

    response_data = response.json()
    print(response_data["data"])
    return render(request,'index.html')
