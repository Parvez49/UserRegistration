import requests
from django.conf import settings
from django.shortcuts import redirect, render



def home(request):
    return render(request,'home.html')

def loginUser(request):
    return render(request,'index.html')


import requests
from django.conf import settings
from django.shortcuts import redirect

def authenticate_with_provider(request, provider):
    # Check if the provider is supported
    if provider not in settings.SOCIAL_AUTH_PROVIDERS:
        return redirect('/auth/accounts/login/')  # Redirect to home page or show an error message

    # Get the provider's configuration from settings
    provider_config = settings.SOCIAL_AUTH_PROVIDERS[provider]

    # Redirect the user to the OAuth2 consent screen of the selected provider
    base_url = provider_config['AUTHORIZATION_URL']
    params = {
        'client_id': provider_config['CLIENT_ID'],
        'redirect_uri': request.build_absolute_uri(f'/auth/{provider}/callback/'),
        'response_type': 'code',
        'scope': provider_config['SCOPE'],
    }
    auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return redirect(auth_url)

def provider_callback(request, provider):
    # Check if the provider is supported
    if provider not in settings.SOCIAL_AUTH_PROVIDERS:
        return redirect('/auth/accounts/login/')  # Redirect to home page or show an error message

    # Handle the callback from the selected provider after user consent
    code = request.GET.get('code')

    # Get the provider's configuration from settings
    provider_config = settings.SOCIAL_AUTH_PROVIDERS[provider]

    # Exchange the authorization code for an access token
    token_url = provider_config['TOKEN_URL']
    data = {
        'code': code,
        'client_id': provider_config['CLIENT_ID'],
        'client_secret': provider_config['CLIENT_SECRET'],
        'redirect_uri': request.build_absolute_uri(f'/auth/{provider}/callback/'),
        'grant_type': 'authorization_code',
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()

    # Get user information using the access token
    user_info_url = provider_config['USER_INFO_URL']
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    

    return redirect('/')  # Redirect to home page or any other desired URL

"""
def google_authenticate(request):
    # Redirect the user to Google's OAuth2 consent screen
    base_url = 'https://accounts.google.com/o/oauth2/auth'
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri('/auth/google/callback/'),
        'response_type': 'code',
        'scope': 'openid email profile',
    }
    auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return redirect(auth_url)

def google_callback(request):
    # Handle the callback from Google after user consent
    code = request.GET.get('code')

    # Exchange the authorization code for an access token
    token_url = 'https://accounts.google.com/o/oauth2/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': request.build_absolute_uri('/auth/google/callback/'),
        'grant_type': 'authorization_code',
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()

    # Get user information using the access token
    user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    print(user_info)

    # Handle the user data as per your requirements
    # For example, you can create a user account or log the user in.

    # user_info contains user details like email, name, etc.
    # You can use this data to create a user account or log the user in.

    return redirect('/')  # Redirect to home page or any other desired URL
"""