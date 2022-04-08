from django.contrib.auth import authenticate
from .backends import CaseInsensitiveModelBackend
from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.utils.translation import gettext_lazy as _


class UserRegistrationSerializer (serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': 'True'}
        }

    def save (self) :

        _email = self.validated_data['email'].lower()

        if User.objects.filter(email = _email).exists() :
            print("Error")
            raise serializers.ValidationError({'Error':'Email already exists'})
        
        user = User (
            email = _email, 
        )

       
        password = self.validated_data['password']
        password2 = self.validated_data['password2']


        if password != password2 :
            raise serializers.ValidationError({'Error' : 'Passwords must match.'})
    
        
        user.set_password(password)
        user.save()

        user_account = UserAccount (user = user, email= _email )
        user_account.save()

        return user

class UserLoginserializer(serializers.Serializer):

    username = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    
    def validate(self, attrs):
        email = attrs.get('username').lower()
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user

        token = Token.objects.get_or_create(user = user)[0].key

        attrs['token'] = token
        return attrs

class UserResetPasswordserializer(serializers.Serializer):
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    newpassword = serializers.CharField(
        label=_("NewPassword"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    def validate(self, attrs):
        request=self.context.get('request')
        email = request.user.email
        password = attrs.get('password')
        newpassword = attrs.get('newpassword')

        if email and password:
            user = authenticate(request=request,username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to Reset Password with invalid password.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "password" and be logged in.')
            raise serializers.ValidationError(msg, code='authorization')

        user.set_password(newpassword)
        user.save()
        return user
        

