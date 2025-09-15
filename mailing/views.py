from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

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


@method_decorator(cache_page(60 * 5), name="dispatch")
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


@method_decorator(cache_page(60 * 5), name="dispatch")
class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "mailing/client_detail.html"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientCreateView(CreateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("client_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


@method_decorator(cache_page(60 * 5), name="dispatch")
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


@method_decorator(cache_page(60 * 5), name="dispatch")
class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing/message_detail.html"


class MessageCreateView(CreateView):
    model = Message
    fields = ["subject", "message"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    fields = ["subject", "message"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")


@method_decorator(cache_page(60 * 5), name="dispatch")
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ["message", "clients"]  # ❌ без start_time, end_time, status
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = "created"  # всегда при создании
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ["message", "clients"]  # ❌ без start_time, end_time, status
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = "created"  # всегда при создании
        return super().form_valid(form)


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")


class MailingSendView(View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.status == "created":
            mailing.start_time = timezone.now()
            mailing.status = "started"
            mailing.save()

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.message,
                    from_email=None,  # возьмётся DEFAULT_FROM_EMAIL
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

        mailing.status = "started"
        mailing.save()

        # после завершения → фиксируем end_time
        mailing.end_time = timezone.now()
        mailing.status = "finished"
        mailing.save()

        messages.success(request, "Рассылка выполнена.")
        return redirect("mailing_detail", pk=mailing.pk)


class AttemptListView(ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"


class StatsView(TemplateView):
    template_name = "mailing/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Все рассылки пользователя
        mailings = Mailing.objects.filter(owner=user)

        # Общее количество рассылок
        total_mailings = mailings.count()

        # Количество успешных и неуспешных попыток
        attempts = Attempt.objects.filter(mailing__owner=user)
        stats_attempts = attempts.aggregate(
            success_count=Count("id", filter=Q(status="success")), failed_count=Count("id", filter=Q(status="failed"))
        )

        # Количество сообщений (одно сообщение может быть в нескольких рассылках):
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
