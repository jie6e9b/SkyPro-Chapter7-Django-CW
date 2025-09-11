from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from models import Attempt, Client, Mailing, Message


# Create your views here.
class IndexView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="started").count()
        context["unique_clients"] = Client.objects.count()
        return context


class ClientListView(ListView):
    model = Client
    template_name = "mailing/client_list.html"


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailing/client_detail.html"


class ClientCreateView(CreateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("client_list")


class ClientUpdateView(UpdateView):
    model = Client
    template_name = "mailing/client_form.html"
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("client_list")


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")


class MessageListView(ListView):
    model = Message
    template_name = "mailing/message_list.html"


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing/message_detail.html"


class MailingCreateView(CreateView):
    model = Mailing
    fields = ["start_time", "end_time", "status", "message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ["start_time", "end_time", "status", "message", "clients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing_list")


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")


class AttemptListView(ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
