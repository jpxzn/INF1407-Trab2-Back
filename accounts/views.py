from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (
    AlterarSenhaSerializer,
    CadastroSerializer,
    PerfilSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordRequestSerializer,
)

import secrets
from .models import PasswordResetCode

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class WhoAmIView(APIView):
    """
    Retorna os dados básicos do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Identificar usuário autenticado",
        description=(
            "Retorna os dados do usuário associado ao token JWT enviado."
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "is_staff": {"type": "boolean"},
                },
            },
        },
        tags=["Autenticação"],
    )
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_staff": request.user.is_staff,
            }
        )
    
class CadastroView(APIView):
    """
    Cria um novo usuário e seu perfil de aluno.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Cadastrar usuário",
        description=(
            "Cria um usuário do Django e um perfil de aluno "
            "associado a ele."
        ),
        request=CadastroSerializer,
        responses={
            201: CadastroSerializer,
            400: dict,
        },
        tags=["Autenticação"],
    )
    def post(self, request):
        serializer = CadastroSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class AlterarSenhaView(APIView):
    """
    Altera a senha do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Alterar senha",
        description=(
            "Altera a senha do usuário autenticado após "
            "confirmar a senha atual."
        ),
        request=AlterarSenhaSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": (
                            "Senha alterada com sucesso."
                        ),
                    },
                },
            },
            400: dict,
            401: dict,
        },
        tags=["Autenticação"],
    )
    def put(self, request):
        serializer = AlterarSenhaSerializer(
            instance=request.user,
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "detail": "Senha alterada com sucesso."
            },
            status=status.HTTP_200_OK,
        )
    
class PerfilView(APIView):
    """
    Consulta e atualiza o perfil do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Consultar perfil",
        description=(
            "Retorna os dados do usuário autenticado. "
            "Peso e altura são retornados apenas para alunos."
        ),
        responses={
            200: PerfilSerializer,
            401: dict,
        },
        tags=["Autenticação"],
    )
    def get(self, request):
        serializer = PerfilSerializer(
            request.user,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Atualizar perfil",
        description=(
            "Atualiza parcialmente os dados do usuário. "
            "Peso e altura podem ser atualizados apenas por alunos."
        ),
        request=PerfilSerializer,
        responses={
            200: PerfilSerializer,
            400: dict,
            401: dict,
        },
        tags=["Autenticação"],
    )
    def patch(self, request):
        serializer = PerfilSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
class PasswordResetView(APIView):
    """
    Solicita e confirma a recuperação de senha.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Solicitar redefinição de senha",
        description=(
            "Recebe o e-mail do usuário, gera um código "
            "temporário e envia as instruções de recuperação."
        ),
        request=ResetPasswordRequestSerializer,
        responses={
            200: dict,
            400: dict,
        },
        tags=["Autenticação"],
    )
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email__iexact=email,
        ).first()

        # Retornamos a mesma mensagem mesmo se o e-mail
        # não existir, evitando revelar usuários cadastrados.
        if user is None:
            return Response(
                {
                    "detail": (
                        "Se o e-mail estiver cadastrado, "
                        "as instruções serão enviadas."
                    )
                },
                status=status.HTTP_200_OK,
            )

        PasswordResetCode.objects.filter(
            user=user,
            used=False,
        ).update(
            used=True,
        )

        code = secrets.token_urlsafe(16)

        PasswordResetCode.objects.create(
            user=user,
            code=code,
        )

        context = {
            "username": user.username,
            "email": user.email,
            "token": code,
        }

        html_message = render_to_string(
            "email/password_reset_email.html",
            context,
        )

        text_message = render_to_string(
            "email/password_reset_email.txt",
            context,
        )

        message = EmailMultiAlternatives(
            subject="Redefinição de senha do GymControl",
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        message.attach_alternative(
            html_message,
            "text/html",
        )

        message.send()

        return Response(
            {
                "detail": (
                    "Se o e-mail estiver cadastrado, "
                    "as instruções serão enviadas."
                )
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Confirmar redefinição de senha",
        description=(
            "Valida o código recebido e define "
            "uma nova senha para o usuário."
        ),
        request=ResetPasswordConfirmSerializer,
        responses={
            200: dict,
            400: dict,
        },
        tags=["Autenticação"],
    )
    def put(self, request):
        serializer = ResetPasswordConfirmSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        code = serializer.validated_data["code"]

        reset_code = PasswordResetCode.objects.filter(
            code=code,
            used=False,
        ).select_related(
            "user",
        ).first()

        if reset_code is None:
            return Response(
                {
                    "detail": (
                        "Código inválido ou já utilizado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reset_code.is_expired():
            reset_code.used = True
            reset_code.save(
                update_fields=["used"],
            )

            return Response(
                {
                    "detail": "O código expirou."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = reset_code.user
        new_password = serializer.validated_data[
            "new_password"
        ]

        try:
            validate_password(
                new_password,
                user=user,
            )
        except DjangoValidationError as error:
            return Response(
                {
                    "new_password": list(error.messages)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(
            new_password,
        )

        user.save(
            update_fields=["password"],
        )

        reset_code.used = True

        reset_code.save(
            update_fields=["used"],
        )

        return Response(
            {
                "detail": "Senha redefinida com sucesso."
            },
            status=status.HTTP_200_OK,
        )