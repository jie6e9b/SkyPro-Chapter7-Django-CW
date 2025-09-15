# users/forms.py
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    """Логин по email (регистр не учитывается)."""

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            return username.lower().strip()
        return username


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя по email."""

    class Meta(UserCreationForm.Meta):
        model = User
        # только реальные поля модели User
        fields = ("email", "phone", "avatar")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            return email.lower().strip()
        return email


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования профиля пользователя (например, в админке)."""

    class Meta:
        model = User
        fields = ("email", "phone", "avatar")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            return email.lower().strip()
        return email
