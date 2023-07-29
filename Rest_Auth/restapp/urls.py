

from django.urls import path
from .views import create_profile, login_user, logout_user, user_data, account_verify
from . import views


urlpatterns = [
    path('register/',create_profile,name="create_profile"),
    path('verify/<str:token>/',account_verify),
    path('login/',login_user),
    path('logout', logout_user, name="lgout"),
    path('data/',user_data),
    path('request-password-reset/', views.request_password_reset, name='request-password-reset'),

    path('reset-password/<str:token>/', views.reset_password, name='reset-password'),
]    
