from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.defaultPath, name="defaultPath"),
    path("api/signup/", views.signup, name="signup"),
    path("api/login/", views.login, name="login"),


    # Post-related paths
    path('service/api/authors/<path:author_serial>/posts/', views.create_post, name='create_post'),
    path('service/api/authors/<path:author_serial>/posts/all/', views.get_all_posts, name='get_all_posts'),
    path('service/api/authors/<path:author_serial>/posts/<path:post_serial>', views.post_detail, name='post_detail'),

    # Follow request paths
    path('service/api/authors/<uuid:author_uuid>/send_follow_request/', views.send_follow_request, name='send_follow_request'),
    path('service/api/authors/<uuid:author_uuid>/accept_follow_request/', views.accept_follow_request, name='accept_follow_request'),
    path('service/api/authors/<uuid:author_uuid>/decline_follow_request/', views.decline_follow_request, name='decline_follow_request'),
    path('service/api/authors/follow_requests/', views.get_follow_requests, name='get_follow_requests'),
    path('service/api/authors/pending_requests/', views.get_pending_requests, name='get-pending-requests'),
    path('service/api/authors/<uuid:author_uuid>/remove_follow_request/', views.remove_follow_request, name='remove-follow-request'),

    # Fetch all authors path
    path('service/api/authors/', views.get_all_authors, name='get_all_authors'),
    
    path('service/api/authors/<str:author_id>/unfollow/', views.unfollow_author, name='unfollow_author'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
