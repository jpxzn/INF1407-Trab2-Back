from django.urls import path
from .views import WhoAmIView, CadastroView

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
]