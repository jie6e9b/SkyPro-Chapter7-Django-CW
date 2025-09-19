from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .mixins import ManagerOrOwnerMixin
from .models import Attempt, Client, Mailing, Message


@method_decorator(cache_control(public=True, max_age=300), name="dispatch")
class IndexView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="started").count()
        context["unique_clients"] = Client.objects.count()
        return context


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


# Используем ManagerOrOwnerMixin вместо ручной проверки в get_queryset
class ClientDetailView(LoginRequiredMixin, ManagerOrOwnerMixin, DetailView):
    model = Client
    template_name = "mailing/client_detail.html"


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Используем ManagerOrOwnerMixin
class ClientUpdateView(LoginRequiredMixin, ManagerOrOwnerMixin, UpdateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Используем ManagerOrOwnerMixin
class ClientDeleteView(LoginRequiredMixin, ManagerOrOwnerMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


# Используем ManagerOrOwnerMixin
class MessageDetailView(LoginRequiredMixin, ManagerOrOwnerMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "message"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Используем ManagerOrOwnerMixin
class MessageUpdateView(LoginRequiredMixin, ManagerOrOwnerMixin, UpdateView):
    model = Message
    fields = ["subject", "message"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Используем ManagerOrOwnerMixin
class MessageDeleteView(LoginRequiredMixin, ManagerOrOwnerMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


# Используем ManagerOrOwnerMixin
class MailingDetailView(LoginRequiredMixin, ManagerOrOwnerMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ["message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = "created"
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        form.fields["message"].queryset = Message.objects.filter(owner=user)
        form.fields["clients"].queryset = Client.objects.filter(owner=user)
        return form


# Используем ManagerOrOwnerMixin
class MailingUpdateView(LoginRequiredMixin, ManagerOrOwnerMixin, UpdateView):
    model = Mailing
    fields = ["message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = "created"
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        form.fields["message"].queryset = Message.objects.filter(owner=user)
        form.fields["clients"].queryset = Client.objects.filter(owner=user)
        return form


# Используем ManagerOrOwnerMixin
class MailingDeleteView(LoginRequiredMixin, ManagerOrOwnerMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")


# Используем ManagerOrOwnerMixin для проверки доступа к рассылке
class MailingSendView(LoginRequiredMixin, ManagerOrOwnerMixin, View):
    model = Mailing  # Добавляем модель для работы миксина

    def get_object(self):
        # Переопределяем для получения объекта по pk из URL
        return get_object_or_404(self.model, pk=self.kwargs["pk"])

    def get(self, request, pk):
        # Теперь миксин автоматически проверит права доступа
        mailing = self.get_object()

        if mailing.status == "created":
            mailing.start_time = timezone.now()
            mailing.status = "started"
            mailing.save()

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.message,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                Attempt.objects.create(
                    mailing=mailing, status="success", server_response="OK", attempt_time=timezone.now()
                )
            except Exception as e:
                print(f"❌ Ошибка отправки на {client.email}: {e}")
                Attempt.objects.create(
                    mailing=mailing, status="failed", server_response=str(e), attempt_time=timezone.now()
                )

        mailing.end_time = timezone.now()
        mailing.status = "finished"
        mailing.save()

        messages.success(request, "Рассылка выполнена.")
        return redirect("mailing_detail", pk=mailing.pk)


class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Attempt.objects.all()
        return Attempt.objects.filter(mailing__owner=user)


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        mailings = Mailing.objects.filter(owner=user)
        total_mailings = mailings.count()

        attempts = Attempt.objects.filter(mailing__owner=user)
        stats_attempts = attempts.aggregate(
            success_count=Count("id", filter=Q(status="success")), failed_count=Count("id", filter=Q(status="failed"))
        )

        unique_messages = mailings.values("message").distinct().count()

        context.update(
            {
                "total_mailings": total_mailings,
                "success_attempts": stats_attempts["success_count"],
                "failed_attempts": stats_attempts["failed_count"],
                "unique_messages": unique_messages,
            }
        )
        return context
