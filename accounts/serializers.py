from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

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
    
class AlterarSenhaSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password_confirmation = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "A senha atual está incorreta."
            )

        return value

    def validate(self, data):
        new_password = data["new_password"]
        new_password_confirmation = data[
            "new_password_confirmation"
        ]

        if new_password != new_password_confirmation:
            raise serializers.ValidationError(
                {
                    "new_password_confirmation": (
                        "As novas senhas não coincidem."
                    )
                }
            )

        if data["current_password"] == new_password:
            raise serializers.ValidationError(
                {
                    "new_password": (
                        "A nova senha deve ser diferente "
                        "da senha atual."
                    )
                }
            )

        user = self.context["request"].user

        try:
            validate_password(
                password=new_password,
                user=user,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {
                    "new_password": list(error.messages)
                }
            ) from error

        return data

    def update(self, instance, validated_data):
        instance.set_password(
            validated_data["new_password"]
        )

        instance.save(
            update_fields=["password"]
        )

        return instance