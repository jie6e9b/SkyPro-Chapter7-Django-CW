import pytest
from django.contrib.auth import get_user_model

from mailing.models import Client, Mailing, Message

User = get_user_model()


@pytest.mark.django_db
def test_create_client():
    user = User.objects.create(email="test@example.com")
    client = Client.objects.create(email="client@example.com", full_name="Test Client", owner=user)
    assert client.email == "client@example.com"
    assert client.owner == user


@pytest.mark.django_db
def test_create_message():
    user = User.objects.create(email="test@example.com")
    msg = Message.objects.create(subject="Hello", body="World", owner=user)
    assert "Hello" in str(msg)


@pytest.mark.django_db
def test_create_mailing():
    user = User.objects.create(email="test@example.com")
    msg = Message.objects.create(subject="Hello", body="World", owner=user)
    mailing = Mailing.objects.create(message=msg, owner=user, status="created")
    assert mailing.status == "created"
