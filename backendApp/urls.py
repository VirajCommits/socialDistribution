from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView
from rest_framework import permissions

# from .views import TestRemoteNodeConnectionView

# from .views import TestRemoteNodeConnectionView

schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version="v1",
        description="API documentation for your project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path("", views.defaultPath, name="defaultPath"),
    path("api/signup/", views.signup, name="signup"),
    path("api/login/", views.login, name="login"),
    # Swagger paths
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # API paths
    path(
        "api/authors/<path:author_serial>/posts/",
        views.create_post,
        name="create_post",
    ),
    path(
        "api/authors/<path:author_serial>/posts/all/",
        views.get_all_posts,
        name="get_all_posts",
    ),
    path(
        "api/authors/<path:author_serial>/posts/<path:post_serial>",
        views.post_detail,
        name="post_detail",
    ),
    path(
        "api/posts/<uuid:post_id>/comments/",
        views.stream_page_comments,
        name="stream_page_comments",
    ),
    path(
        "api/posts/<uuid:post_id>/likes/",
        views.stream_page_likes,
        name="stream_page_likes",
    ),
    path(
        "api/posts/<uuid:post_id>/comment/",
        views.post_comment,
        name="post_comment",
    ),
    path("api/posts/<uuid:post_id>/like/", views.like_post, name="like_post"),
    path(
        "api/posts/<uuid:post_id>/repost/",
        views.repost_post,
        name="repost_post",
    ),
    # Follow request paths
    path(
        "api/authors/<uuid:author_uuid>/send_follow_request/",
        views.send_follow_request,
        name="send_follow_request",
    ),
    path(
        "api/authors/<uuid:author_uuid>/accept_follow_request/",
        views.accept_follow_request,
        name="accept_follow_request",
    ),
    path(
        "api/authors/<uuid:author_uuid>/decline_follow_request/",
        views.decline_follow_request,
        name="decline_follow_request",
    ),
    path(
        "api/authors/follow_requests/",
        views.get_follow_requests,
        name="get_follow_requests",
    ),
    path(
        "api/authors/pending_requests/",
        views.get_pending_requests,
        name="get-pending-requests",
    ),
    path(
        "api/authors/<uuid:author_uuid>/remove_follow_request/",
        views.remove_follow_request,
        name="remove-follow-request",
    ),
    # Fetch all authors path
    path(
        "api/authors/",
        views.get_all_authors,
        name="get_all_authors",
    ),
    # Stream and follow-related paths
    path(
        "api/authors/<path:author_id>/stream/",
        views.stream_page,
        name="stream_page",
    ),
    path(
        "api/authors/<str:author_id>/unfollow/",
        views.unfollow_author,
        name="unfollow_author",
    ),
    path(
        "api/posts/<uuid:post_id>/",
        views.get_post_by_link,
        name="get_post_by_link",
    ),
    path(
        "api/authors/<uuid:author_uuid>/relationship/",
        views.check_relationship_status,
        name="check-relationship-status",
    ),
    path(
        "api/authors/<uuid:author_uuid>/stats/",
        views.get_author_stats,
        name="get-author-stats",
    ),
    # path(
    #     "api/authors/<uuid:author_uuid>/followers/",
    #     views.get_author_followers,
    #     name="get-author-followers",
    # ),
    path(
        "api/authors/<uuid:author_uuid>/following/",
        views.get_author_following,
        name="get-author-following",
    ),
    path(
        "api/authors/<uuid:author_uuid>/friends/",
        views.get_author_friends,
        name="get-author-friends",
    ),
    path(
        "api/comments/<uuid:comment_id>/like/",
        views.like_comment,
        name="like_comment",
    ),
    path(
        "api/comments/<uuid:comment_id>/likes/",
        views.comment_likes,
        name="comment_likes",
    ),
    path(
        "api/authors/<uuid:author_uuid>/",
        views.update_author_profile,
        name="update_author_profile",
    ),
    path(
        "api/authors/<uuid:author_uuid>/public/",
        views.PublicAuthorProfileView.as_view(),
        name="public-author-profile",
    ),
    path(
        "api/authors/<uuid:author_uuid>/stats/public/",
        views.PublicAuthorStatsView.as_view(),
        name="public-author-stats",
    ),
    path(
        "api/authors/<uuid:author_uuid>/post/public/",
        views.PublicPostsView.as_view(),
        name="public-author-posts",
    ),
    # path(
    #     "nodes/<int:pk>/test_connection/",
    #     TestRemoteNodeConnectionView.as_view(),
    #     name="test_connection",
    # ),
    path(
        'api/authors/<str:author_serial>/inbox/', 
        views.inbox_handler, 
        name='inbox'
    ),

    path(
        'api/authors/<str:author_serial>/sendRemoteRequest/', 
        views.send_follow_request_to_remote_authors, 
        name='send_follow_request_to_remote_authors'
    ),


    path(
    "api/authors/<path:author_serial>/followers/",
    views.followers_handler,
    name="followers_handler"
    ),
    path(
        "api/authors/<path:author_serial>/followers/<path:foreign_author_fqid>/",
        views.specific_follower_handler,
        name="specific_follower_handler"
    ),
    path(
        "stream", TemplateView.as_view(template_name="index.html"), name="stream"
    ),
    path(
        "api/sync_remote_authors/",
        views.sync_remote_authors,
        name="sync_remote_authors",
    ),
    
    path('api/connected-nodes/', views.connected_nodes, name='connected_nodes'),
    path('verify-connection/', views.verify_node_connection, name='verify_node_connection'),
    path(
        "posts/<uuid:post_id>/",
        TemplateView.as_view(template_name="index.html"),
        name="post_detail",
    ),
    path('api/connected-nodes/', views.connected_nodes, name='connected_nodes'),
    # Catch-all route for Vue frontend
    re_path(
        r"^(?!api|admin|swagger|static|media).*$",
        TemplateView.as_view(template_name="index.html"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
