from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
from .models import Author
from django.shortcuts import get_object_or_404
from django.utils import timezone

def defaultPath(request):
    return render(request, "index.html")

@api_view(['GET'])
def sample_data(request):
    data = {
        'message': 'Hello from Django to Vue!'
    }
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request, author_serial):
    # Ensure the authenticated user is the author
    if not hasattr(request.user, 'author') or request.user.author.id != author_serial:
        return Response({'error': 'You are not authorized to create posts for this author.'}, status=status.HTTP_403_FORBIDDEN)
    
    data = request.data.copy()
    
    # Add the author data to the request data
    author = get_object_or_404(Author, id=author_serial)
    data['author'] = {
        'id': author.id,
        'type': 'author',
        'host': author.host,
        'displayName': author.displayName,
        'page': author.page,
        'github': author.github,
        'profileImage': author.profileImage
    }

    # Set the published date
    data['published'] = timezone.now().isoformat()

    serializer = PostSerializer(data=data)
    if serializer.is_valid():
        post = serializer.save()
        response_serializer = PostSerializer(post)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)