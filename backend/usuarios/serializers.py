from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.models import Group

from .models import Usuario


ROLES_GESTIONABLES = ("Administrador", "Auditor", "Usuario consulta")


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
        choices=ROLES_GESTIONABLES,
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

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Campos que un administrador puede modificar en un usuario."""

    password = serializers.CharField(write_only=True, min_length=8, required=False)
    rol = serializers.ChoiceField(choices=ROLES_GESTIONABLES, write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "rol",
        )

    def update(self, instance, validated_data):
        rol = validated_data.pop("rol", None)
        password = validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()

        if rol:
            grupos = Group.objects.filter(name__in=ROLES_GESTIONABLES)
            instance.groups.remove(*grupos)
            instance.groups.add(Group.objects.get(name=rol))

        return instance
