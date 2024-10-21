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

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("project/", include("backendApp.urls")),
    # path(
    #     "service/api/authors/<path:author_id>/posts/<slug:post_id>/comments/",
    #     views.create_comment,
    #     name="create_comment",
    # ),
    # path(
    #     "service/api/authors/<path:author_id>/posts/<slug:post_id>/comments/list/",
    #     views.get_comments,
    #     name="get_comments",
    # ),
    # path(
    #     "service/api/authors/<path:author_id>/posts/<slug:post_id>/like/",
    #     views.like_post,
    #     name="like_post",
    # ),
    # path(
    #     "service/api/authors/<path:author_id>/posts/<slug:post_id>/likes/",
    #     views.get_likes,
    #     name="get_likes",
    # ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
