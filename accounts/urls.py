from django.urls import path
from .views import (
    AlterarSenhaView,
    CadastroView,
    PerfilView,
    WhoAmIView,
)

app_name = "accounts"

urlpatterns = [
    path(
        "whoami/",
        WhoAmIView.as_view(),
        name="whoami",
    ),
    
    path(
        "register/",
        CadastroView.as_view(),
        name="register",
    ),

    path(
        "change-password/",
        AlterarSenhaView.as_view(),
        name="change-password",
    ),

    path(
        "profile/",
        PerfilView.as_view(),
        name="profile",
    ),
]