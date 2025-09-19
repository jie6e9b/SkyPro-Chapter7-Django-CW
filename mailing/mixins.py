from django.contrib.auth.mixins import UserPassesTestMixin


class OwnerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь является владельцем объекта.
    Используется когда только владелец может получить доступ.
    """

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return obj.owner == user


class ManagerOrOwnerMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь менеджер или владелец объекта.
    Используется в большинстве случаев, когда менеджеры могут видеть все объекты.
    """

    def test_func(self):
        user = self.request.user

        # Менеджеры могут все
        if user.groups.filter(name="Managers").exists():
            return True

        # Владелец может работать со своими объектами
        obj = self.get_object()
        return hasattr(obj, "owner") and obj.owner == user


class OwnerFilterMixin:
    """
    Миксин для автоматической фильтрации QuerySet по владельцу.
    Используется в ListView для показа только объектов пользователя.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.groups.filter(name="Managers").exists():
            return queryset

        return queryset.filter(owner=user)
