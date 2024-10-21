from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.defaultPath, name="defaultPath"),
    path("api/test/", views.sample_data ,name="sample_data"),
    # path('service/api/authors/<path:author_serial>/posts/', views.create_post, name='create_post'),
    # path('service/api/authors/<path:author_serial>/posts/all/', views.get_all_posts, name='get_all_posts'),
    # path('service/api/authors/<path:author_serial>/posts/<path:post_serial>', views.post_detail, name='create_post'),
    # New URLs for comments and likes
    path('service/api/authors/<slug:author_id>/posts/<slug:post_id>/comments/', views.create_comment, name='create_comment'),
    path('service/api/authors/<slug:author_id>/posts/<slug:post_id>/comments/list/', views.get_comments, name='get_comments'),
    path('service/api/authors/<slug:author_id>/posts/<slug:post_id>/like/', views.like_post, name='like_post'),
    path('service/api/authors/<slug:author_id>/posts/<slug:post_id>/likes/', views.get_likes, name='get_likes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)