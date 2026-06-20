from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Exercicio
from .serializers import ExercicioSerializer


class ExerciciosView(APIView):
    """
    Lista todos os exercícios ou cria um novo exercício.
    """

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