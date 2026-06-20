from django.urls import path
from .views import (
    ExercicioView,
    ExerciciosView,
    TreinoExercicioView,
    TreinoExerciciosView,
    TreinoView,
    TreinosView,
)

app_name = "GymControl"

urlpatterns = [
    path(
        "exercicios/",
        ExerciciosView.as_view(),
        name="exercicios",
    ),

    path(
        "exercicios/<int:pk>/",
        ExercicioView.as_view(),
        name="exercicio",
    ),

    path(
        "treinos/",
        TreinosView.as_view(),
        name="treinos",
    ),

    path(
        "treinos/<int:pk>/",
        TreinoView.as_view(),
        name="treino",
    ),

    path(
        "treinos/<int:treino_pk>/exercicios/",
        TreinoExerciciosView.as_view(),
        name="treino-exercicios",
    ),

    path(
        (
            "treinos/<int:treino_pk>/"
            "exercicios/<int:pk>/"
        ),
        TreinoExercicioView.as_view(),
        name="treino-exercicio",
    ),
]