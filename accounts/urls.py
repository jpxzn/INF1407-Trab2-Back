from django.urls import path
from .views import WhoAmIView

app_name = "accounts"

urlpatterns = [
    path(
        "whoami/",
        WhoAmIView.as_view(),
        name="whoami",
    ),
]