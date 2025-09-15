from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")
