from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Attempt, Mailing


class Command(BaseCommand):
    help = "Отправка рассылки по ID"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID рассылки")

    def handle(self, *args, **kwargs):
        mailing_id = kwargs["mailing_id"]
        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылка {mailing_id} не найдена"))
            return

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                Attempt.objects.create(
                    mailing=mailing, status="success", server_response="OK", attempt_time=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f"Успешно отправлено {client.email}"))
            except Exception as e:
                Attempt.objects.create(
                    mailing=mailing, status="failed", server_response=str(e), attempt_time=timezone.now()
                )
                self.stdout.write(self.style.ERROR(f"Ошибка при отправке {client.email}: {e}"))

        mailing.status = "started"
        mailing.save()
