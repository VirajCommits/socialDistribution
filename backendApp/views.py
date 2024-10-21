from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Author, Post, FollowRequest
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import AuthorSerializer, PostSerializer, FollowRequestSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticated]

    # Send a follow request
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_follow_request(self, request, uuid=None):
        current_author = request.user.author
        target_author = get_object_or_404(Author, uuid=uuid)

        if current_author == target_author:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if follow request already exists
        if FollowRequest.objects.filter(actor=current_author, object=target_author).exists():
            return Response({'detail': 'Follow request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new follow request
        follow_request = FollowRequest.objects.create(
            actor=current_author,
            object=target_author,
            summary=f"{current_author.displayName} wants to follow {target_author.displayName}"
        )
        return Response(FollowRequestSerializer(follow_request).data, status=status.HTTP_201_CREATED)

    # Accept a follow request
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept_follow_request(self, request, uuid=None):
        current_author = request.user.author
        requesting_author = get_object_or_404(Author, uuid=uuid)

        follow_request = get_object_or_404(FollowRequest, actor=requesting_author, object=current_author)
        current_author.followers.add(requesting_author)  # Add to followers
        follow_request.delete()  # Remove the follow request
        return Response({'detail': 'Follow request accepted.'}, status=status.HTTP_200_OK)

    # Decline a follow request
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def decline_follow_request(self, request, uuid=None):
        current_author = request.user.author
        requesting_author = get_object_or_404(Author, uuid=uuid)

        follow_request = get_object_or_404(FollowRequest, actor=requesting_author, object=current_author)
        follow_request.delete()  # Remove the follow request
        return Response({'detail': 'Follow request declined.'}, status=status.HTTP_200_OK)

    # Unfollow an author
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, uuid=None):
        current_author = request.user.author
        target_author = get_object_or_404(Author, uuid=uuid)

        current_author.following.remove(target_author)
        return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)

    # Get current author's profile
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response(AuthorSerializer(request.user.author).data)

    # Get the list of follow requests received by the author
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def follow_requests(self, request, uuid=None):
        current_author = get_object_or_404(Author, uuid=uuid)
        requests = FollowRequest.objects.filter(object=current_author)
        serializer = FollowRequestSerializer(requests, many=True, context={'request': request})
        return Response(serializer.data)
    

class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]

class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticated]

class AuthorUpdateView(generics.UpdateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticated]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(unlisted=False)
    serializer_class = PostSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.author)


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Get the logged-in user's Author profile via user relationship
            try:
                author = Author.objects.get(user=user)
                # Redirect to /author/<uuid>
                return redirect(reverse('author_detail', kwargs={'uuid': author.uuid}))
            except Author.DoesNotExist:
                return render(request, 'login.html', {'error': 'Author profile not found.'})
        else:
            # Add proper redirection for login failure
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')


# Modify CustomAuthToken to return author details
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        author = Author.objects.get(user=token.user)
        return Response({
            'token': token.key,
            'uuid': author.uuid,  # Add UUID of the author for the frontend
        })

@login_required
def author_detail(request, uuid):
    try:
        author = Author.objects.get(uuid=uuid)
    except Author.DoesNotExist:
        return render(request, 'error.html', {'message': 'Author not found'})

    return render(request, 'author_detail.html', {'author': author})

def logout_view(request):
    logout(request)
    return redirect('login')
