from django.db import models

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)


class Aluno(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ],
    )

    altura = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0.50),
            MaxValueValidator(2.80),
        ],
    )

    def __str__(self) -> str:
        return self.user.username


class Treino(models.Model):
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
    )

    nome = models.CharField(
        max_length=50,
    )

    def __str__(self) -> str:
        return f"{self.nome} - {self.aluno}"


class Exercicio(models.Model):
    class Musculo(models.TextChoices):
        ABDOMEN = "abdomen", "Abdômen"
        AEROBICO = "aerobico", "Aeróbico"
        PEITO = "peito", "Peito"
        TRICEPS = "triceps", "Tríceps"
        BICEPS = "biceps", "Bíceps"
        ANTEBRACO = "antebraco", "Antebraço"
        COSTAS = "costas", "Costas"
        ANTERIOR_PERNA = "anterior_perna", "Anterior de perna"
        POSTERIOR_PERNA = "posterior_perna", "Posterior de perna"
        OMBRO = "ombro", "Ombro"
        PANTURRILHA = "panturrilha", "Panturrilha"

    nome = models.CharField(
        max_length=100,
    )

    link_video = models.URLField(
        blank=True,
    )
    
    musculo_trabalhado = models.CharField(
        max_length=30,
        choices=Musculo.choices,
    )

    def __str__(self) -> str:
        return self.nome


class TreinoExercicio(models.Model):
    treino = models.ForeignKey(
        Treino,
        on_delete=models.CASCADE,
    )

    exercicio = models.ForeignKey(
        Exercicio,
        on_delete=models.CASCADE,
    )

    qtd_series = models.PositiveIntegerField()
    qtd_repeticoes = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.exercicio} - {self.treino}"
