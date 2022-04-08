from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth import authenticate
from .utils import generate_token
import threading
from notifications.views import reset_successful, verify_email, login_email, welcome_email,forgot_password_email
import random



from notifications.utils import send_notification

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def create_otp(email):
    otp = random.randint(10000,99999)
    
    if UserOtp.objects.filter(email = email).exists(): 
        UserOtp.objects.get(email = email).delete()
    
    user_otp = UserOtp(email = email, code = otp)
    user_otp.save()
    return user_otp.code

def verify_otp(email,otp):
    if UserOtp.objects.filter(email = email).exists(): 
        user_otp = UserOtp.objects.get(email = email)
        if str(otp) == str(user_otp.code) :
            user_otp.delete()
            return True
        else :
            return False
    else:
        return False


# Sign Up View
class SignUp (APIView):
    permission_classes = [AllowAny]
    # serializer_class = UserRegistrationSerializer
    def post(self, request):

        # print(request.path)

        # serializer = self.serializer_class(data = request.data)

        data = {}

        _email = request.data['email']

       
        password = request.data['password']
        phone = request.data['phone']
        firstname = request.data['firstname']
        lastname = request.data['lastname']
        expo_push_token = request.data['expoPT']

        if User.objects.filter(email=_email).exists():

            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            email=_email,
        )

        user.set_password(password)
        user.save()

        user_account = UserAccount(
            user=user, email=user.email, phone=phone, firstname=firstname, lastname=lastname, expo_push_token=expo_push_token)
        user_account.save()

        # send_activation_email(user, request)

        data['response'] = 'Registered Successfully'
        try : 
            
            verify_email(user_account,create_otp(user.email), "Verify Your Account")
        except:
            print('Failed notification')

        return Response(data)

class LogIn (APIView):

    permission_classes = [AllowAny]

    serializer_class = UserLoginserializer

    def post(self, request):

        data = {}
        data['token'] = ''
        expo_push_token = request.data['expoPT']

        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({'Invalid login credentials'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        data['email'] = user.email
        data['token'] = serializer.validated_data['token']

        user_account = UserAccount.objects.get(user=user)

        prev_token = user_account.expo_push_token
        user_account.expo_push_token = expo_push_token
        user_account.save()

        if (not user.verified):
            verify_email(user_account,create_otp(user.email), "Verify Your Account")
            return Response({'Account not verified'}, status=status.HTTP_400_BAD_REQUEST)
        try :
            if prev_token != user_account.expo_push_token :
                login_email(user_account, "You Logged In")
        except : 
            print ("failed mail")
        return Response(data)

class Logout(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class UpdateDetails(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        user = request.user

        account = UserAccount.objects.get(user=user)

        data = request.data

        account.firstname = data['firstname']
        account.lastname = data['lastname']
        
       
        account.save(update_fields=['firstname', 'lastname'])

        return Response(status=status.HTTP_200_OK)

# Send otp for forgot password
class ForgotPasswordOTP(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        email = request.data['email']

        if User.objects.filter(email = email).exists():
            user_account = UserAccount.objects.get(email = email)

            otp = create_otp(email) 
            forgot_password_email(user_account,otp,'Forgot Password')
        else : 
            return Response({"Account doesn't exist"}, status = status.HTTP_400_BAD_REQUEST)
        return Response({'success'})
        
class FogotPassword(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        otp = request.data['otp']
        email = request.data['email']
        newpassword = request.data['password']
      
        if verify_otp(email,otp) == True:
        
            if User.objects.filter(email = email).exists() :
                user = User.objects.get( email = email,  )
                user.set_password(newpassword)
                user.save()
                user_account = UserAccount.objects.get(user = user)
                reset_successful(user_account, "Password Changed")
            
                return Response({'Successfully changed'}, status=status.HTTP_200_OK)
            else:
                return Response({f'Account with {email} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'Code is invalid or has expired'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        otp = request.data['otp']
        email = request.data['email']
      
        if verify_otp(email,otp) == True:
        
            if User.objects.filter(email = email).exists() :
                user = User.objects.get( email = email )
                user.verified = True
                user.save()

                user_account = UserAccount.objects.get(user = user)
                welcome_email(user_account, "Timmy From Trakka")
                send_notification(user, "Signup Successful ✅", "Welcome to Trakka🎉")
                return Response({'Successfully verified'}, status=status.HTTP_200_OK)
            else:
                return Response({f'Account with {email} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'Code is invalid or has expired'}, status=status.HTTP_400_BAD_REQUEST) 

class ResetPassword(APIView):
    permission_classes = [IsAuthenticated]
 
    def post(self,request):
        email = request.user.email
        password = request.data['password']
        newpassword = request.data['newpassword']

        try:
            if email and password:
                user = authenticate(username=email, password=password)

                if not user : 

                    return Response({'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(newpassword)
                user.save()
                user_account = UserAccount.objects.get(user = user)
                reset_successful(user_account, "Password Changed")
            
            else :
                return Response({'Unable to Change Password'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Successfully changed'}, status=status.HTTP_200_OK)
        except:
            return Response({'Unable to Change Password'}, status=status.HTTP_400_BAD_REQUEST)
