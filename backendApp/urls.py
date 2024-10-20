from django.urls import path
from . import views
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    # Default path is the login page
    path('', views.login_view, name='login'),
    path('author/<uuid:uuid>/', views.author_detail, name='author_detail'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/authors/', views.AuthorListView.as_view(), name='author-list'),
    path('api/authors/<uuid:uuid>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('api/authors/<uuid:uuid>/edit/', views.AuthorUpdateView.as_view(), name='author-update'),
    path('api/auth/login/', auth_views.obtain_auth_token, name='api-token-auth'),
]
