from django.urls import path
from . import views


urlpatterns = [
    path("", views.defaultPath, name="defaultPath"),
    path("api/test/", views.sample_data ,name="sample_data"),
]