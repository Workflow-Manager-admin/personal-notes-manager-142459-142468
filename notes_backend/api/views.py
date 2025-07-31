from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserSerializer, RegisterSerializer, Note
from .serializers import NoteSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_summary="Health check endpoint.",
    operation_description="Returns a confirmation that the backend service is running.",
    responses={200: openapi.Response('Successful health check', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
    ))}
)
@api_view(['GET'])
def health(request):
    """
    Health check endpoint.
    Returns: { "message": "Server is up!" }
    """
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_summary="Register a new user.",
    operation_description="Registers a user account. Required fields in body:\n- username (str)\n- password (str)\n- email (optional, str)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Desired username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address', nullable=True),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ),
    responses={
        201: openapi.Response(
            "User created successfully", UserSerializer
        ),
        400: openapi.Response(
            "Invalid input"
        )
    },
    tags=['auth']
)
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
@swagger_auto_schema(
    method='post',
    operation_summary="Obtain JWT tokens for valid credentials.",
    operation_description="Takes username and password, returns JWT tokens if credentials are valid.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user')
        }
    ),
    responses={
        200: openapi.Response(
            description="JWT tokens returned",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        401: openapi.Response(
            description="Invalid credentials"
        )
    },
    tags=['auth']
)
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
@swagger_auto_schema(
    method='post',
    operation_summary="Log out user (blacklist JWT refresh).",
    operation_description="Log out a user by blacklisting the JWT refresh token. Requires the refresh token in body.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist (logout)')
        }
    ),
    responses={
        205: openapi.Response("Logout successful"),
        400: openapi.Response("Bad request")
    },
    tags=['auth']
)
@api_view(['POST'])
def logout(request):
    """
    Log out a user by blacklisting the refresh token (for JWT auth).
    Required field: {"refresh": "string"}
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

    @swagger_auto_schema(
        operation_summary="List notes",
        operation_description="List all notes owned by authenticated user. Supports ?search, ?ordering query parameters.",
        tags=["notes"]
    )
    def list(self, request, *args, **kwargs):
        """List notes for authenticated user."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a note",
        operation_description="Create a personal note for the authenticated user.",
        tags=["notes"]
    )
    def create(self, request, *args, **kwargs):
        """Create note owned by user."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get note",
        operation_description="Retrieve a note by ID for the authenticated user.",
        tags=["notes"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific note."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update note",
        operation_description="Update (replace) a note by ID for the user.",
        tags=["notes"]
    )
    def update(self, request, *args, **kwargs):
        """Update (replace) a note."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update note",
        operation_description="Update (patch) part of a note for the user.",
        tags=["notes"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Update (patch) note fields."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete note",
        operation_description="Delete a note by ID for the user.",
        tags=["notes"]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a note."""
        return super().destroy(request, *args, **kwargs)

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
