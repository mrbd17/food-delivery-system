from django.shortcuts import render
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from ..google_service import GoogleAuthService
from ..serializers import RegisterSerializer, LoginSerializer, GoogleAuthSerializer
from django.views.decorators.clickjacking import xframe_options_exempt
import logging
logger = logging.getLogger(__name__)


User = get_user_model()
@xframe_options_exempt
def auth_page(request):
    get_token(request)
    return render(request, "auth/auth.html")


from django.http import JsonResponse

def google_callback(request):
    return JsonResponse({"message": "Google callback reached"})

    
class GoogleAuth(APIView):
    permission_classes= [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
    
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = serializer.validated_data['token']
            mode = serializer.validated_data['mode']

            service = GoogleAuthService()
            user = service.authenticate(token, mode)

            auth_login(request, user)

            return Response({
                'success': True,
                'message': f'Welcome {user.first_name or "back"}!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name,
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.warning(f"Google auth error: {str(e)}")
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Unexpected error in google_auth: {str(e)}")
            return Response(
                {'success': False, 'message': 'Server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        email = request.data.get("email")
        inactive_user = User.objects.filter(
            email=email, is_active=False
        ).first()

        if inactive_user:
            return Response(
                {"success":True, "message":"Verifiction code sent to your email"},
                status=status.HTTP_409_CONFLICT
            )

        serializer = RegisterSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))[0]
            return Response(
                {
                    "success":False,
                 "message": first_error,
                 "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response(
            {"success": True, "message":"Account created successfully"},
            status=status.HTTP_201_CREATED
        )
    
class LoginAPIView(APIView):
    permission_classes=[AllowAny]
    throttle_classes = [AnonRateThrottle]
    def post(self,request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success":False,
                 "message": serializer.errors.get(
                    "non_field_errors",
                    ["Validation errors"]
                )[0],
                "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.validated_data['user']
        auth_login(request, user)
        return Response(
            {
            'success': True,
            "user":{"id":user.id,"email":user.email}
            },
            status=status.HTTP_200_OK
        )
class LogoutAPIView(APIView):
    premission_classes = [IsAuthenticated]

    def post(self,request):
        auth_logout(request)
        return Response(
            {
                "success":True,
                "message":"Logged out successfully"
            },
            status=status.HTTP_200_OK
        )
        
        
