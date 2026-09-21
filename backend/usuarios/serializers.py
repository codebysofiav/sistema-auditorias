from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Usuario


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["roles"] = list(user.groups.values_list("name", flat=True))
        return token


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    rol = serializers.ChoiceField(
        choices=["Administrador", "Auditor", "Usuario consulta"],
        write_only=True,
    )

    class Meta:
        model = Usuario
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "rol",
        )

    def create(self, validated_data):
        from django.contrib.auth.models import Group

        rol = validated_data.pop("rol")
        password = validated_data.pop("password")

        usuario = Usuario.objects.create_user(password=password, **validated_data)

        grupo = Group.objects.get(name=rol)
        usuario.groups.add(grupo)

        return usuario


class UsuarioSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "roles",
        )
        read_only_fields = fields

    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))
