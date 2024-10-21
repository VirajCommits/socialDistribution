from django.urls import path
from . import views


urlpatterns = [
    path("", views.defaultPath, name="defaultPath"),
    path("api/test/", views.sample_data ,name="sample_data"),
    path("api/signup/", views.SignupView.as_view(), name="signup"),
    path("api/login/", views.LoginView.as_view(), name="login"),
]