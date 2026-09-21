from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions
from .models import Usuario


from .serializers import EmailTokenObtainPairSerializer, UsuarioCreateSerializer, UsuarioSerializer

class EsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name="Administrador").exists()
        )

class UsuarioCreateView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioCreateSerializer
    permission_classes = [EsAdministrador]

class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class UsuarioAutenticadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Sesion cerrada. El cliente debe descartar los tokens JWT."})
