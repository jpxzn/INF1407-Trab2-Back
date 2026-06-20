from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .models import Exercicio, Treino
from .serializers import ExercicioSerializer, TreinoSerializer


class ExerciciosView(APIView):
    """
    Lista todos os exercícios ou cria um novo exercício.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar exercícios",
        description="Retorna todos os exercícios cadastrados.",
        responses={200: ExercicioSerializer(many=True)},
        tags=["Exercícios"],
    )
    def get(self, request):
        exercicios = Exercicio.objects.all()

        serializer = ExercicioSerializer(
            exercicios,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar exercício",
        description="Cadastra um novo exercício.",
        request=ExercicioSerializer,
        responses={
            201: ExercicioSerializer,
            400: dict,
        },
        tags=["Exercícios"],
    )
    def post(self, request):

        if not request.user.is_staff:
            return Response(
                {
                    "detail": (
                        "Apenas administradores podem "
                        "cadastrar exercícios."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ExercicioSerializer(
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


class ExercicioView(APIView):
    """
    Consulta, atualiza ou exclui um exercício específico.
    """

    permission_classes = [IsAuthenticated]

    def get_exercicio(self, pk):
        try:
            return Exercicio.objects.get(pk=pk)
        except Exercicio.DoesNotExist:
            return None

    @extend_schema(
        summary="Consultar exercício",
        description="Retorna um exercício pelo seu identificador.",
        responses={
            200: ExercicioSerializer,
            404: dict,
        },
        tags=["Exercícios"],
    )
    def get(self, request, pk):
        exercicio = self.get_exercicio(pk)

        if exercicio is None:
            return Response(
                {"detail": "Exercício não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExercicioSerializer(exercicio)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Atualizar exercício",
        description="Atualiza todos os dados de um exercício.",
        request=ExercicioSerializer,
        responses={
            200: ExercicioSerializer,
            400: dict,
            404: dict,
        },
        tags=["Exercícios"],
    )
    def put(self, request, pk):

        if not request.user.is_staff:
            return Response(
                {
                    "detail": (
                        "Apenas administradores podem "
                        "editar exercícios."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        exercicio = self.get_exercicio(pk)

        if exercicio is None:
            return Response(
                {"detail": "Exercício não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExercicioSerializer(
            exercicio,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Excluir exercício",
        description="Exclui um exercício cadastrado.",
        responses={
            204: None,
            404: dict,
        },
        tags=["Exercícios"],
    )
    def delete(self, request, pk):

        if not request.user.is_staff:
            return Response(
                {
                    "detail": (
                        "Apenas administradores podem "
                        "excluir exercícios."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        exercicio = self.get_exercicio(pk)

        if exercicio is None:
            return Response(
                {"detail": "Exercício não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        exercicio.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
    
class TreinosView(APIView):
    """
    Lista os treinos disponíveis para o usuário ou cria um novo treino.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar treinos",
        description=(
            "Administradores visualizam todos os treinos. "
            "Alunos visualizam somente os próprios treinos."
        ),
        responses={
            200: TreinoSerializer(many=True),
        },
        tags=["Treinos"],
    )
    def get(self, request):
        if request.user.is_staff:
            treinos = Treino.objects.all()
        else:
            treinos = Treino.objects.filter(
                aluno__user=request.user,
            )

        serializer = TreinoSerializer(
            treinos,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar treino",
        description=(
            "Cria um treino para um aluno. "
            "A operação é permitida apenas para administradores."
        ),
        request=TreinoSerializer,
        responses={
            201: TreinoSerializer,
            400: dict,
            403: dict,
        },
        tags=["Treinos"],
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {
                    "detail": (
                        "Apenas administradores podem "
                        "cadastrar treinos."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TreinoSerializer(
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
    
class TreinoView(APIView):
    """
    Consulta, atualiza ou exclui um treino específico.
    """

    permission_classes = [IsAuthenticated]

    def get_treino(self, pk, user):
        if user.is_staff:
            return Treino.objects.filter(pk=pk).first()

        return Treino.objects.filter(
            pk=pk,
            aluno__user=user,
        ).first()

    @extend_schema(
        summary="Consultar treino",
        description=(
            "Administradores podem consultar qualquer treino. "
            "Alunos podem consultar somente os próprios treinos."
        ),
        responses={
            200: TreinoSerializer,
            404: dict,
        },
        tags=["Treinos"],
    )
    def get(self, request, pk):
        treino = self.get_treino(
            pk,
            request.user,
        )

        if treino is None:
            return Response(
                {"detail": "Treino não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TreinoSerializer(treino)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Atualizar treino",
        description=(
            "Atualiza os dados de um treino. "
            "Permitido somente para administradores."
        ),
        request=TreinoSerializer,
        responses={
            200: TreinoSerializer,
            400: dict,
            403: dict,
            404: dict,
        },
        tags=["Treinos"],
    )
    def put(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {
                    "detail": (
                        "Apenas administradores podem "
                        "editar treinos."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        treino = self.get_treino(
            pk,
            request.user,
        )

        if treino is None:
            return Response(
                {"detail": "Treino não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TreinoSerializer(
            treino,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Excluir treino",
        description=(
            "Exclui um treino. "
            "Permitido somente para administradores."
        ),
        responses={
            204: None,
            403: dict,
            404: dict,
        },
        tags=["Treinos"],
    )
    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {
                    "detail": (
                        "Apenas administradores podem "
                        "excluir treinos."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        treino = self.get_treino(
            pk,
            request.user,
        )

        if treino is None:
            return Response(
                {"detail": "Treino não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        treino.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )