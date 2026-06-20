from rest_framework import serializers
from .models import Aluno, Exercicio, Treino, TreinoExercicio


class AlunoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Aluno
        fields = [
            "id",
            "user",
            "username",
            "email",
            "peso",
            "altura",
        ]

        read_only_fields = [
            "user",
        ]


class TreinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treino
        fields = [
            "id",
            "aluno",
            "nome",
        ]


class ExercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercicio
        fields = [
            "id",
            "nome",
            "link_video",
            "musculo_trabalhado",
        ]


class TreinoExercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreinoExercicio
        fields = [
            "id",
            "treino",
            "exercicio",
            "qtd_series",
            "qtd_repeticoes",
        ]