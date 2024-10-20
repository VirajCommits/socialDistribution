from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Author
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from .serializers import AuthorSerializer

class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]

class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.AllowAny]

class AuthorUpdateView(generics.UpdateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'uuid'
    permission_classes = [permissions.IsAuthenticated]

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
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')

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
