from django.urls import path
from .views import ExerciciosView, ExercicioView

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
]