from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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