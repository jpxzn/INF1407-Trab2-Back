from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

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
    
class PerfilSerializer(serializers.ModelSerializer):
    peso = serializers.DecimalField(
        source="aluno.peso",
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=1,
        max_value=500,
    )

    altura = serializers.DecimalField(
        source="aluno.altura",
        max_digits=3,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=0.50,
        max_value=2.80,
    )

    tipo_usuario = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "date_joined",
            "tipo_usuario",
            "peso",
            "altura",
        ]

        read_only_fields = [
            "id",
            "date_joined",
            "tipo_usuario",
        ]

    def get_tipo_usuario(self, user):
        if user.is_staff or user.is_superuser:
            return "admin"

        return "aluno"

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "O nome de usuário não pode ficar vazio."
            )

        return value

    def validate_email(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "O e-mail não pode ficar vazio."
            )

        existing_user = User.objects.exclude(
            pk=self.instance.pk
        ).filter(
            email__iexact=value
        ).exists()

        if existing_user:
            raise serializers.ValidationError(
                "Este e-mail já está sendo utilizado."
            )

        return value

    def validate(self, data):
        request = self.context["request"]
        user = request.user

        is_admin = (
            user.is_staff or
            user.is_superuser
        )

        aluno_data = data.get("aluno")

        if is_admin and aluno_data:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Peso e altura são campos exclusivos "
                        "de usuários alunos."
                    )
                }
            )

        if not is_admin:
            try:
                user.aluno
            except Aluno.DoesNotExist as error:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "O perfil de aluno não foi encontrado."
                        )
                    }
                ) from error

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        aluno_data = validated_data.pop(
            "aluno",
            {},
        )

        instance.username = validated_data.get(
            "username",
            instance.username,
        )

        instance.email = validated_data.get(
            "email",
            instance.email,
        )

        instance.save(
            update_fields=[
                "username",
                "email",
            ]
        )

        is_admin = (
            instance.is_staff or
            instance.is_superuser
        )

        if not is_admin and aluno_data:
            aluno = instance.aluno

            if "peso" in aluno_data:
                aluno.peso = aluno_data["peso"]

            if "altura" in aluno_data:
                aluno.altura = aluno_data["altura"]

            aluno.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)

        is_admin = (
            instance.is_staff or
            instance.is_superuser
        )

        if is_admin:
            data.pop("peso", None)
            data.pop("altura", None)

        return data