from rest_framework import permissions
from .models import Auditoria  # agrega este import al inicio del archivo permissions.py



def user_in_group(user, *group_names):
    return user.groups.filter(name__in=group_names).exists()


def get_auditoria_from_object(obj):
    if isinstance(obj, Auditoria):   # <-- esta línea es la nueva
        return obj

    if hasattr(obj, "auditoria"):
        return obj.auditoria

    if hasattr(obj, "plan_auditoria"):
        return obj.plan_auditoria.auditoria

    if hasattr(obj, "plan"):
        return obj.plan.auditoria

    if hasattr(obj, "accion"):
        return obj.accion.plan.auditoria

    if hasattr(obj, "hallazgo"):
        return obj.hallazgo.auditoria

    return None


def auditor_is_assigned(user, auditoria):
    if not auditoria:
        return False

    return auditoria.auditoriaauditor_set.filter(auditor=user, activo=True).exists()


class AuditoriaRolePermission(permissions.BasePermission):
    """
    Permiso base por roles de Django Groups.

    - Administrador: acceso completo.
    - Auditor: lectura y escritura.
    - Usuario consulta: solo lectura.
    """

    admin_group = "Administrador"
    auditor_group = "Auditor"
    consulta_group = "Usuario consulta"

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user_in_group(user, self.admin_group):
            return True

        if request.method in permissions.SAFE_METHODS:
            return user_in_group(user, self.auditor_group, self.consulta_group)

        return user_in_group(user, self.auditor_group)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user_in_group(user, self.admin_group):
            return True

        if getattr(view, "admin_write_only", False) and request.method not in permissions.SAFE_METHODS:
            return False

        if user_in_group(user, self.consulta_group):
            return request.method in permissions.SAFE_METHODS

        if user_in_group(user, self.auditor_group):
            auditoria = get_auditoria_from_object(obj)
            if getattr(obj._meta, "model_name", "") == "unidadauditada":
                return True
            if not auditoria and request.method in permissions.SAFE_METHODS:
                return getattr(obj._meta, "model_name", "") == "unidadauditada"
            return auditor_is_assigned(user, auditoria)

        return False
