import pytest
from django.urls import reverse

from sell_it_app.models import User, Category, Newsletter


# main page test


@pytest.mark.django_db
def test_index_page_status_code(client):
    response = client.get('/')
    assert response.status_code == 200

# login page


@pytest.mark.django_db
def test_login_page_status_code(client):
    response = client.get('/login/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_user_ok(client):
    password = 'testtesttest'
    if len(password) >= 6:
        response = client.post('/login/', {'username': 'test', 'password': f'{password}'})
        assert response.status_code == 200


@pytest.mark.django_db
def test_login_user_invalid(client):
    response = client.post('/login/', {'username': 'test', f'password': 'a'})
    assert response.status_code == 200
    assert 'Invalid username or password.' in response.content.decode()


# logout

@pytest.mark.django_db
def test_logout_user_ok(client):
    response = client.post('/logout/', {'username': 'test', 'password': 'passpass'})
    assert response.status_code == 302


# register page
@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username='Rafal', email='test@gmail.com', password='secret_password')
    user.save()
    assert user.username == 'Rafal'
    assert user.email == 'test@gmail.com'
    assert User.objects.get(username=user.username) == user
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_create_user_invalid():
    password2 = 'sh'
    password = 'short'
    username = 'test1'
    if password == password2 and len(password) > 6:
        user = User.objects.create_user(username=username, email='short', password=password)
        user.save()
    else:
        assert User.objects.count() == 0
        assert User.objects.filter(username=username).exists() is False


# admin test


@pytest.mark.django_db
def test_admin_panel_ok(client):
    admin = User.objects.create_superuser(
        username="admin",
        password="adminadminadmin",
        is_staff=True,
        is_superuser=True,
    )
    client.login(username="admin", password="adminadminadmin")
    admin_url = reverse('admin:index')
    response = client.get(admin_url)
    assert response.status_code == 200
    assert User.objects.count() == 1
    assert User.objects.filter(username="admin").exists() is True


@pytest.mark.django_db
def test_admin_panel_not_ok(client):
    user = User.objects.create_user(
        username="admin",
        password="adminadminadmin",
        is_staff=False,
        is_superuser=False,
    )
    admin_url = reverse('admin:index')
    response = client.post(admin_url)
    assert response.status_code != 200


# dashboard tests


@pytest.mark.django_db
def test_dashboard_status_code(client):
    response = client.post('/dashboard/', {'username': 'test', 'password': 'testtesttest'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_dashboard_status_wrong_code(client):
    response = client.get('/dashboard/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_category_status_code_ok(client):
    category = Category.objects.create(name='test', description='test')
    response = client.get("/category/1/")
    assert response.status_code == 200
    assert Category.objects.filter(name=category.name).count() == 1


@pytest.mark.django_db
def test_category_status_code_not_exists(client):
    response = client.get('/category/1/')
    assert response.status_code == 404
    assert Category.objects.filter(pk=1).exists() is False



@pytest.mark.django_db




@pytest.mark.django_db
def test_newsletter_ok(client):
    response = client.get(reverse('newsletter'))
    assert response.status_code == 200


@pytest.mark.django_db


@pytest.mark.django_db


@pytest.mark.django_db
def test_abous_us_status_code(client):
    response = client.get(reverse('about-us'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_newsletter_register_email_ok(client):
    response = client.post('/newsletter/', {'email': 'test@gmail.com'})
    assert response.status_code == 302
    assert Newsletter.objects.count() == 1


@pytest.mark.django_db
def test_newsletter_register_email_exists(client):
    email = Newsletter.objects.create(email='rafal.czerwik@gmail')
    email.save()
    response = client.post('/newsletter/', {'email': 'rafal.czerwik@gmail.com'})
    if email.email == 'rafal.czerwik@gmail.com':
        assert Newsletter.objects.filter(email='rafal.czerwik@gmail.com').count() == 1
        assert response.status_code == 302
        assert 'Email already registered!' in response.content.decode()
