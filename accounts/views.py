from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (
    AlterarSenhaSerializer,
    CadastroSerializer,
    PerfilSerializer,
)

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