from django.urls import path
from .views import GPTView

urlpatterns = [
    path("api/gpt/", GPTView.as_view(), name="gpt")
]
