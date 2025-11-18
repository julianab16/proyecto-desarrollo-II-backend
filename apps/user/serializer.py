from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "dni",
            "phone_number",
            "password",
            "role",
            "is_staff",
        ]
        read_only_fields = ["id", "username", "is_staff"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "dni",
            "phone_number",
            "password",
            "role",
            "is_staff",
        ]
        read_only_fields = ["id", "is_staff"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        role = validated_data.get("role", "user")

        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            raise serializers.ValidationError(
                {"password": "Este campo es obligatorio."}
            )
        if role in ["ADMINISTRADOR", "VENDEDOR"]:
            user.is_staff = True
        user.save()
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Este correo ya está registrado.")
        return value
