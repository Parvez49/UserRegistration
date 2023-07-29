from django.shortcuts import render
from .serializers import ProfileSerializer
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.core.mail import send_mail


@csrf_exempt
@api_view(['POST'])
def create_profile(request):
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        email=serializer.data['user']['email']
        user=User.objects.get(email=email)
        user.is_active=False
        user.save()

        # ----------JSON Web Token--------------
        payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'iat': datetime.datetime.utcnow()
    }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response() 
        response.set_cookie(key='activation', value=token, httponly=True) # Set cookie
        
        # ----------Emain Send------------
        email_subject="Activate your account"
        message=f"http://127.0.0.1:8000/reset-password/{token}"
        send_mail(email_subject,message,settings.EMAIL_HOST_USER,[email])
        response.data="Activation token has been sent in your gmail"

        return response
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def account_verify(request,token):
    #usertkn=request.data['token']
    #print(usertkn)
 
    tkn=request.COOKIES.get('activation')
    print("tkn",tkn)
    if not tkn:
        raise AuthenticationFailed('Failed')
    
    if token==tkn:
        try:
            payload = jwt.decode(tkn, 'secret', algorithms=['HS256'])
            print(payload)
        except ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except DecodeError:
            raise AuthenticationFailed('Unauthenticated!')
    

        user=User.objects.get(id=payload['id'])
        user.is_active=True
        user.save()
        
        return Response("Your account Activated")
    else:
        raise AuthenticationFailed('Failed')

    




from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import jwt, datetime
from .serializers import UserSerializer

@api_view(['POST'])
def login_user(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email).first()

    if user is None:
        raise AuthenticationFailed('User not found!')
    if user.is_active==False:
        raise AuthenticationFailed('Check Gmail')

    if not user.check_password(password):
        raise AuthenticationFailed('Incorrect password!')     
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')

    response = Response()

    response.set_cookie(key='jwt', value=token, httponly=True)
    #response.data=UserSerializer(user).data
    
    response.data = {'jwt': token}

    return response

@api_view(['GET'])
def logout_user(request):
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
        'message': 'success'
    }
    return response


from jwt.exceptions import ExpiredSignatureError, DecodeError
from .models import Profile
@api_view(['GET'])
def user_data(request):
    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed('Unauthenticated!')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')

    user = User.objects.filter(id=payload['id']).first()
    prdata=Profile.objects.filter(user=user).first()

    serializer = ProfileSerializer(prdata)
    return Response(serializer.data)



import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
import datetime
from .serializers import PasswordResetSerializer

# ...

@csrf_exempt
@api_view(['POST'])
def request_password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(email=serializer.validated_data['email'])
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Expiration after 1 hour
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        reset_link = f"http://127.0.0.1:8000/reset-password/{token}"

        # Send the reset link to the user's email
        email_subject = "Password Reset"
        message = f"Click the link below to reset your password:\n{reset_link}"
        send_mail(email_subject, message, settings.EMAIL_HOST_USER, [user.email])

        return Response("Password reset link has been sent to your email.")
    return Response(serializer.errors, status=400)


@csrf_exempt
@api_view(['POST'])
def reset_password(request,token):
    #token = request.data.get('token')
    new_password = request.data.get('new_password')
    confirm_new_password = request.data.get('confirm_new_password')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        return Response("Token has expired.", status=400)
    except DecodeError:
        return Response("Invalid token.", status=400)

    user = User.objects.get(id=payload['id'])

    if new_password == confirm_new_password:
        user.set_password(new_password)
        user.save()
        return Response("Password has been reset successfully.")
    else:
        return Response("New passwords do not match.", status=400)




