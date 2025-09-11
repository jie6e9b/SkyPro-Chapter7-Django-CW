from django.contrib import admin
from django.urls import include, path

from mailing.views import IndexView

urlpatterns = [
    # Админка
    path("admin/", admin.site.urls),
    # Главная страница
    path("", IndexView.as_view(), name="index"),
    # Пользователи (регистрация, профиль и т.д.)
    path("users/", include("users.urls")),
    # Рассылки
    path("mailing/", include("mailing.urls")),
]
