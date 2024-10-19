from django.urls import path
from . import views


urlpatterns = [
    path("", views.defaultPath, name="defaultPath"),
    path("api/test/", views.sample_data ,name="sample_data"),
    path('service/api/authors/<path:author_serial>/posts/', views.create_post, name='create_post'),
    path('service/api/authors/<path:author_serial>/posts/all/', views.get_all_posts, name='get_all_posts'),
    path('service/api/authors/<path:author_serial>/posts/<path:post_serial>', views.post_detail, name='create_post'),
    
]