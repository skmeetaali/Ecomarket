from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'role',
        ]
        read_only_fields = ['id']

    def validate_password(self, value):
        # Validate against Django's configured password rules.
        validate_password(value)
        return value

    def validate_role(self, value):
        if value not in [User.Role.BUYER, User.Role.SELLER]:
            raise serializers.ValidationError(
                "Only buyer and seller registration is allowed."
            )
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', User.Role.BUYER)

        user = User.objects.create_user(
            **validated_data,
            role=role,
        )

        if role == User.Role.SELLER:
            user.seller_status = User.SellerStatus.PENDING
            user.save(update_fields=['seller_status'])

        return user
    
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data['username'],
            password=data['password'],
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        data['user'] = user
        return data