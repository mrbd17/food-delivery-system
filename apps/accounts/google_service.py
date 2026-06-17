from django.contrib.auth import get_user_model
from google.auth.transport import requests
from google.oauth2 import id_token
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class GoogleAuthService:

    def __init__(self, client_id=None):
        self.client_id = client_id or os.getenv('GOOGLE_CLIENT_ID')

    def verify_token(self, token):

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.client_id
            )

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')

            return idinfo

        except ValueError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise

    def extract_user_data(self, idinfo):

        email = idinfo.get('email')
        name = idinfo.get('name', '')

        if not email:
            raise ValueError('Email not provided by Google')

        return {
            'email': email,
            'name': name,
            'username': email.split('@')[0]
        }

    def handle_login(self, user_data):

        email = user_data['email']

        try:
            user = User.objects.get(email=email)
            logger.info(f"User login: {email}")
            return user

        except User.DoesNotExist:
            raise ValueError(f"User not found. Create an account first.")

    def handle_signup(self, user_data):

        email = user_data['email']
        name = user_data['name']
        username = user_data['username']

        if User.objects.filter(email=email).exists():
            raise ValueError("Email already registered. Sign in instead.")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name,
                password=''
            )
            logger.info(f"New user created via Google: {email}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise ValueError("Failed to create user account")

    def authenticate(self, token, mode):

        idinfo = self.verify_token(token)
        user_data = self.extract_user_data(idinfo)

        if mode == 'login':
            user = self.handle_login(user_data)
        elif mode == 'signup':
            user = self.handle_signup(user_data)
        else:
            raise ValueError("Invalid mode")

        return user