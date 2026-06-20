from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from .serializers import CadastroSerializer

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
