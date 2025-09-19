from django import template

register = template.Library()


@register.filter
def is_manager(user):
    """Проверяет, является ли пользователь менеджером"""
    return user.groups.filter(name="Managers").exists()


@register.filter
def can_edit_object(obj, user):
    """Проверяет, может ли пользователь редактировать объект"""
    return obj.owner == user or user.is_superuser or user.groups.filter(name="Managers").exists()
