
from django.urls import path, include
from .views import *

urlpatterns = [
    path('' ,  home  , name="home"),
    path('register' , register_attempt , name="register_attempt"),
    path('accounts/login/' , login_attempt , name="login_attempt"),
    path('token' , token_send , name="token_send"),
    path('verify/<auth_token>' , verify , name="verify"),

    path('accounts/logout/',user_logout,name="user_logout"),
    path('forgot-password/',ForgotPassword,name="forgot_password")
]
