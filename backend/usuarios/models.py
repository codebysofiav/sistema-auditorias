from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# CAMPOS DE USUARIO QUE TRAE POR DEFECTO DJANGO
# USUARIO
# ├── id                  ← Django
# ├── username            ← Django
# ├── password            ← Django, almacenada como hash
# ├── first_name          ← Django
# ├── last_name           ← Django
# ├── email               ← Django
# ├── is_active           ← Django
# ├── date_joined         ← Django
# ├── last_login          ← Django
