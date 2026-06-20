from django.contrib.auth.models import User
from rest_framework import serializers

from GymControl.models import Aluno


class CadastroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirmation = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirmation",
        ]

        read_only_fields = [
            "id",
        ]

    def validate(self, data):
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError(
                {
                    "password_confirmation": (
                        "As senhas não coincidem."
                    )
                }
            )

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirmation")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        Aluno.objects.create(user=user)

        return user