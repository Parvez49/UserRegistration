from django.shortcuts import render, redirect

# Create your views here.

def home(request):
    return render(request , 'home.html')


from django.contrib.auth.models import User
from django.contrib import messages
import uuid
from .models import Profile
from .email_server import validate_email

def register_attempt(request):
    data={"username":"",
          "email":"",
          "password":""}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            data["username"]=username
            data["email"]=email
            data["password"]=password
            if User.objects.filter(username = username).first():
                messages.success(request, 'Username is already registered.')
                #return redirect('/register')
                return render(request , 'register.html',{"data":data})

            if User.objects.filter(email = email).first():
                messages.success(request, 'Email is already registered.')
                #return redirect('/register')
                return render(request , 'register.html',{"data":data})
            if not validate_email(email):
                messages.warning(request, 'Invalid or Inactive email!')
                #return redirect('/register')
                return render(request , 'register.html',{"data":data})

            
            user_obj = User(username = username , email = email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj , auth_token = auth_token)
            profile_obj.save()
            send_mail_after_registration(email , auth_token)
            return redirect('/token')

        except Exception as e:
            print(e)

    
    return render(request , 'register.html',{"data":data})

from django.core.mail import send_mail
from django.conf import settings
def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )


from django.contrib.auth import authenticate,login
def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.success(request, 'User not found.')
            return redirect('/accounts/login')
        
        
        profile_obj = Profile.objects.filter(user = user_obj ).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('/accounts/login')

        user = authenticate(username = username , password = password)
        if user is None:
            messages.success(request, 'Wrong password.')
            return redirect('/accounts/login')
        
        login(request , user)
        return redirect('/')

    return render(request , 'login.html')



    

def token_send(request):
    return render(request , 'token_send.html')


def verify(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
    

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/accounts/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/accounts/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')
    

from django.contrib.auth import logout
def user_logout(request):
    logout(request)
    return redirect("/accounts/login")


def ForgotPassword(request):

    data={'email': ""}
    if request.method=='POST':
        email=request.POST['email']
        data['email']=email
        try:
            if User.objects.filter(email = email).first()==None:
                messages.warning(request, 'Email not Registered!')
                #return redirect('/register')
                return render(request , 'forgot.html',{"data":data})
            else:
                subject = 'Change Password'
                message = f'Click this link to change your password http://127.0.0.1:8000/change_password/'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message , email_from ,recipient_list )

                messages.success(request,"Password change link has been sent your gmail.")
                return render(request,'forgot.html',{"data":data})
        except Exception as e:
            print(e)



    return render(request,"forgot.html",{"data":data})
