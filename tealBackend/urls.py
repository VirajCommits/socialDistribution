"""
URL configuration for tealBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from backendApp import views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("project/", include("backendApp.urls")),
    path(
        "api/authors/<str:author_id>/posts/<str:post_id>/comments/add/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "api/authors/<str:author_id>/posts/<str:post_id>/likes/add/",
        views.like_post,
        name="like_post",
    ),
    path(
        "api/posts/<str:post_id>/public/likes/",
        views.get_likes_for_public_post,
        name="get_likes_for_public_post",
    ),
    path(
        "api/posts/<str:post_id>/comments/",
        views.get_comments_by_post,
        name="get_comments_by_post",
    ),
]
