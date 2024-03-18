import pytest
from django.test import Client

from sell_it_app.models import User, Newsletter


@pytest.fixture
def client():
    client = Client()
    return client


@pytest.fixture
def admin():
    admin = User.objects.create_superuser(
        username="admin",
        password="adminadminadmin",
        is_staff=True,
        is_superuser=True
    )
    return admin


@pytest.fixture
def user():
    user = User.objects.create_user(username="Test", password="testtesttest")
    return user


@pytest.fixture
def newsletter():
    email = Newsletter.objects.create(email="test@gmail.com")
    return email


@pytest.fixture
def listing():
    pass


@pytest.fixture
def avatar():
    pass
