from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from authentication.models import User
from authentication.utils import generate_email_verification_token, send_verification_email, send_password_reset_email


class SignupSerializer(serializers.ModelSerializer):
    password_2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'password_2')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'required': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"detail": str(e)})

        password_2 = attrs.get('password_2')

        if password != password_2:
            raise serializers.ValidationError({"detail": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """
        Override Create method.
        now, user.is_active = False by default.
        Add functionality to send Verification email to user.
        """
        validated_data.pop('password_2')
        user = User.objects.create_user(**validated_data, is_active=False)

        token = generate_email_verification_token(user)

        request = self.context.get('request')
        absolute_uri = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token})
        )

        send_verification_email(user, absolute_uri)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        try:
            refresh = self.token_class(attrs["refresh"])
            refresh.check_blacklist()
        except TokenError:
            raise serializers.ValidationError({"detail": "Token is Invalid or Blacklisted."})
        data = {"access": str(refresh.access_token)}

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            attrs['user'] = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "No user found with this email."})
        return attrs

    def password_reset(self):
        user = self.validated_data['user']
        token = RefreshToken.for_user(user).access_token

        request = self.context.get('request')
        absolute_uri = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'token': token})
        )
        send_password_reset_email(user, absolute_uri)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"detail": str(e)})

        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        token = self.context['view'].kwargs.get('token')
        if not token:
            raise serializers.ValidationError({"detail": "Token is required."})
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(pk=user_id)
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "No user found with this token."})
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})

        return attrs

    def update_password(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        # access_token blacklistshi chagdeba ?!
