from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, UsuarioAutenticadoView, UsuarioCreateView, UsuarioListView

urlpatterns = [
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UsuarioAutenticadoView.as_view(), name="usuario_autenticado"),
    path("usuarios/crear/", UsuarioCreateView.as_view(), name="usuario-crear"),
    path("usuarios/", UsuarioListView.as_view(), name="usuario-listar"),
]
