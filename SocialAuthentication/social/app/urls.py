from django.urls import path
from . import views

urlpatterns = [
    # ... Your other URL patterns ...
    path('auth/<str:provider>/', views.authenticate_with_provider, name='authenticate_with_provider'),
    path('auth/<str:provider>/callback/', views.provider_callback, name='provider_callback'),
    path('',views.home,name="home"),

    path('login/',views.loginUser),
]
