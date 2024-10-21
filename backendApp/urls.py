from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.defaultPath, name="defaultPath"),
    path("api/signup/", views.SignupView.as_view(), name="signup"),
    path("api/login/", views.LoginView.as_view(), name="login"),

    # Post-related paths
    path('service/api/authors/<path:author_serial>/posts/', views.create_post, name='create_post'),
    path('service/api/authors/<path:author_serial>/posts/all/', views.get_all_posts, name='get_all_posts'),
    path('service/api/authors/<path:author_serial>/posts/<path:post_serial>', views.post_detail, name='post_detail'),

    # Follow request paths
    path('service/api/authors/<path:author_serial>/send_follow_request/', views.send_follow_request, name='send_follow_request'),
    path('service/api/authors/<path:author_serial>/accept_follow_request/', views.accept_follow_request, name='accept_follow_request'),
    path('service/api/authors/<path:author_serial>/decline_follow_request/', views.decline_follow_request, name='decline_follow_request'),
    path('service/api/authors/follow_requests/', views.get_follow_requests, name='get_follow_requests'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
