from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserSerializer, RegisterSerializer

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

# Example of a protected endpoint
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notes_list(request):
    """
    List all notes for the logged-in user (placeholder).

    This should be replaced by real notes logic.
    """
    # Example only; replace with actual notes logic.
    # You'd typically query Note.objects.filter(user=request.user)
    return Response({"notes": []})
