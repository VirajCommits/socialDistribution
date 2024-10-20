from django.urls import path, include
from . import views
from rest_framework.authtoken import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, PostViewSet, CustomAuthToken

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    # Default path is the login page
    path('', views.login_view, name='login'),
    path('author/<uuid:uuid>/', views.author_detail, name='author_detail'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/auth/login/', CustomAuthToken.as_view(), name='api-token-auth'),
    path('api/authors/', views.AuthorListView.as_view(), name='author-list'),
    path('api/authors/<uuid:uuid>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('api/authors/<uuid:uuid>/edit/', views.AuthorUpdateView.as_view(), name='author-update'),
]
