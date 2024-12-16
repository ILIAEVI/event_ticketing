from django.contrib.auth import authenticate
from rest_framework import status, generics, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from authentication.serializers import SignupSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, \
    LoginSerializer, LogoutSerializer, RefreshTokenSerializer
from authentication.models import User
from authentication.permissions import NotAuthenticated


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [NotAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["message"] = "Account created successfully. Please check your email to verify your account."

        return response


class VerifyEmailView(APIView):
    permission_classes = [NotAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            token = self.kwargs.get('token')
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)

            if user.is_active:
                return Response({"message": "Account is already active."}, status=status.HTTP_200_OK)
            user.is_active = True
            user.save()

            # !? acces_token is blacklistshi gadatana, meti usafrtxoebistivs....

            return Response({"message": "Account is activated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e), "message": 'Invalid or expired verification link.'},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    permission_classes = [NotAuthenticated]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "Account is Inactive! Activation link is in your email."},
                            status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
        }, status=status.HTTP_200_OK)


class RefreshTokenView(GenericAPIView):
    permission_classes = [NotAuthenticated]
    serializer_class = RefreshTokenSerializer
    www_authenticate_realm = "api"

    def get_authenticate_header(self, request) -> str:
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():

            refresh_token = serializer.validated_data['refresh']
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.password_reset()
        return Response({"message": "Password reset email sent successfully."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update_password()
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)
