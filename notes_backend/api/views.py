from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserSerializer, RegisterSerializer, Note
from .serializers import NoteSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """
    Health check endpoint.
    """
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Register a new user.

    Required fields in body:
    - username (str)
    - password (str)
    - email (optional, str)
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    Obtain JWT tokens for valid credentials.

    Required fields in body:
    - username (str)
    - password (str)
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

# PUBLIC_INTERFACE
@api_view(['POST'])
def logout(request):
    """
    Log out a user by blacklisting the refresh token (for JWT auth).
    Add your notes endpoints, protected below.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
class NoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Notes.

    Only authenticated users can perform CRUD on their own notes.

    Supports searching and filtering notes by "title" and "content" via the `search` query parameter.
    Example: /api/notes/?search=my_text will return notes whose title or content contains "my_text" (case-insensitive substring).

    Query Parameters:
    - search: string. Case-insensitive search for any substring in title or content.
    - ordering: string (e.g., 'created_at', '-updated_at'). Orders the result.

    Note: Only authenticated users will get results for their own notes.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering = ['-updated_at']
    search_fields = ['title', 'content']

    def get_queryset(self):
        """
        Limit notes to those owned by the request user.
        """
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Set note owner as the requesting user.
        """
        serializer.save(owner=self.request.user)
