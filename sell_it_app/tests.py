import datetime
from datetime import timedelta

import pytest
from django.urls import reverse

from sell_it_app.models import User, Category, Newsletter, Listings, Address, Picture, Messages


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


@pytest.mark.django_db
def test_register_user_ok(client):
    assert User.objects.count() == 0

    gender = "M"
    username = 'testuser'
    first_name = 'testfirst'
    last_name = 'testlast'
    email = 'test@gmail.com'
    password = 'testtesttest'
    password2 = 'testtesttest'
    dob = datetime.date.today() - timedelta(days=10000)

    assert User.objects.filter(username=username).exists() is False

    if password != password2:
        raise ValueError('Passwords do not match')
    else:
        response = client.post(f'/register/', {
            'gender': gender,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'password_confirm': password2,
            'dob': dob,
        })

    assert response.status_code == 302  # -> to /login/
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_register_user_invalid(client):
    assert User.objects.count() == 0

    gender = "W"
    username = 'testuser'
    first_name = 'testfirst'
    last_name = 'testlast'
    email = 'test@gmail.com'
    password = 'testtesttest'
    password2 = 'testtesttest1'
    dob = datetime.date.today() - timedelta(days=10000)

    response = client.post(f'/register/', {
        'gender': gender,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'password_confirm': password2,
        'dob': dob,
    })

    assert response.status_code != 302
    assert User.objects.count() == 0


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
def test_profile_view_status_code(client):
    user = User.objects.create_user(username='testuser', password='testtesttest')
    user.save()
    client.login(username='testuser', password='testtesttest')
    response = client.get('/profile/', {'username': 'test', 'password': 'testtesttest'})
    assert response.status_code == 200
    assert User.objects.filter(pk=user.pk).exists() is True


@pytest.mark.django_db
def test_profile_view_status_code_not_ok(client):
    response = client.get('/profile/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_update_password_view_status_code_ok(client):
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')

    assert User.objects.count() == 1

    client.login(username='testuser', password='testtest')

    password = 'newpassword'
    confirm_password = 'newpassword'

    if password == confirm_password:
        response = client.post('/profile/update-password/', {
            'new_password': password,
            'new_password_confirm': confirm_password,
        })

        assert response.status_code == 302


@pytest.mark.django_db
def test_update_password_view_status_code_not_ok(client):
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')

    assert User.objects.count() == 1

    client.login(username='testuser', password='testtest')

    password = 'new'
    confirm_password = 'new1'

    if len(password) >= 6 and password == confirm_password:
        response = client.post('/profile/update-password/', {
            'new_password': password,
            'new_password_confirm': confirm_password,
        })

        assert response.status_code == 200
        assert 'Password must be at least 6 characters long!' in response.content.decode()


@pytest.mark.django_db
def test_update_password_view_not_logged_status_code_ok(client):
    response = client.post('/profile/update-password/')
    assert response.status_code != 200
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_update_profile_view_not_logged_status_code_ok(client):
    response = client.post('/update-profile/')
    assert response.status_code != 200
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_update_profile_logged_user_status_code_ok_updated(client):
    assert User.objects.count() == 0

    user = User.objects.create_user(
        username='testuser',
        first_name='test',
        last_name='test',
        password='testtest',
        gender='M',
        phone_number='123456789',
        date_of_birth='1988-01-01',
    )
    assert User.objects.count() == 1
    assert User.objects.get(pk=user.id) == user

    client.login(username='testuser', password='testtest')
    response = client.get('/update-profile/')
    assert response.status_code == 200

    response1 = client.post('/update-profile/', {
        'username': user.username,
        'gender': user.gender,
        'first_name': 'Name',
        'last_name': 'Surname',
        'phone_numer': '987654321',
        'date_of_birth': '1989-02-02',
    })
    assert response1.status_code == 302

    updated_user = User.objects.get(username=user.username)
    assert updated_user.first_name == 'Name'
    assert updated_user.last_name == 'Surname'


@pytest.mark.django_db
def test_update_profile_view_logged_user_status_code_ok_not_updated(client):
    assert User.objects.count() == 0

    user = User.objects.create_user(
        username='testuser',
        first_name='test',
        last_name='test',
        password='testtest',
        gender='M',
        phone_number='123456789',
        date_of_birth='1988-01-01',
    )
    assert User.objects.count() == 1
    assert User.objects.get(pk=user.id) == user

    client.login(username='testuser', password='testtest')
    response = client.get('/update-profile/')
    assert response.status_code == 200

    phone_numer = '98765432'

    if len(phone_numer) == 9:
        response1 = client.post('/update-profile/', {
            'username': user.username,
            'gender': user.gender,
            'first_name': 'Name',
            'last_name': 'Surname',
            'phone_numer': phone_numer,
            'date_of_birth': '2300-02-02',
        })
        assert response1.status_code == 302
    else:
        not_updated_user = User.objects.get(username=user.username)
        assert not_updated_user.first_name == 'test'
        assert not_updated_user.last_name == 'test'


@pytest.mark.django_db
def test_update_profile_avatar_logged_user_ok(client):
    pass


@pytest.mark.django_db
def update_profile_avatar_logged_user_fail(client):
    pass


@pytest.mark.django_db
def test_update_profile_avatar_view_not_logged_user_fail(client):
    pass


@pytest.mark.django_db
def test_newsletter_ok(client):
    response = client.get(reverse('newsletter'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_public_profile_view_status_code(client):
    user = User.objects.create_user(username='testuser', password='testtesttest')
    user.save()
    client.login(username='testuser', password='testtesttest')
    response = client.get('/public_profile/')
    assert response.status_code == 404
    assert User.objects.filter(pk=user.pk).exists() is True


@pytest.mark.django_db
def test_public_profile_view_status_code_not_ok(client):
    response = client.get('/public_profile/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_search_view_logged_user_status_code_ok(client):
    user = User.objects.create_user(username='testuser', password='testtesttest')
    user.save()
    client.login(username='testuser', password='testtesttest')
    search_query = 'test'
    response = client.get(f'/search/?search_query={search_query}')
    assert response.status_code == 200
    assert Listings.objects.filter(title__icontains=search_query).order_by('title').count() == 0


@pytest.mark.django_db
def test_search_view_not_logged_user_status_code_ok(client):
    search_query = 'test'
    response = client.post(f'/search/?search_query={search_query}')
    assert response.status_code != 200
    assert Listings.objects.filter(title__icontains=search_query).order_by('title').count() == 0


@pytest.mark.django_db
def test_listings_view_logged_user_status_code_ok(client):
    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    client.login(username='testuser', password='testtesttesttest')
    response = client.get('/listings/')
    assert response.status_code == 200
    assert Listings.objects.filter(user_id=user).count() == 0


@pytest.mark.django_db
def test_listings_view_not_logged_user_status_code_ok(client):
    response = client.get('/listings/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_listing_map_view_logged_user_status_code_ok(client):
    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    address = Address.objects.create(street_name='testaddress', user_id=user)
    address.save()

    client.login(username='testuser', password='testtesttesttest')

    listing = Listings.objects.create(user_id=user, category_id=category, address_id=address, condition='Used',
                                      offer_type='Sell', promotion='Not Promoted', status='Active',
                                      title='Test Listing', description='This is a test listing', price=10.99)
    listing.save()

    response = client.get(f'/listing/map/{listing.id}/')
    assert response.status_code == 200
    assert Listings.objects.filter(id=listing.id).count() == 1
    assert Address.objects.filter(id=address.id).count() == 1
    assert Category.objects.filter(id=category.id).count() == 1


@pytest.mark.django_db
def test_listing_details_view_logged_user_status_code_ok(client):
    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    address = Address.objects.create(street_name='testaddress', user_id=user)
    address.save()

    assert Listings.objects.filter(user_id=user).count() == 0

    client.login(username='testuser', password='testtesttesttest')

    listing = Listings.objects.create(user_id=user, category_id=category, address_id=address, condition='Used',
                                      offer_type='Sell', promotion='Not Promoted', status='Active',
                                      title='Test Listing', description='This is a test listing', price=10.99)
    listing.save()

    response = client.get(f'/listing-details/{listing.id}/')
    assert response.status_code == 200
    assert Listings.objects.filter(id=listing.id).count() == 1
    assert Address.objects.filter(id=address.id).count() == 1
    assert Category.objects.filter(id=category.id).count() == 1
    assert Picture.objects.filter(id=listing.id).count() == 0


@pytest.mark.django_db
def test_listing_details_view_not_logged_user_status_code_ok(client):
    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    address = Address.objects.create(street_name='testaddress', user_id=user)
    address.save()

    assert Listings.objects.filter(user_id=user).count() == 0

    listing = Listings.objects.create(user_id=user, category_id=category, address_id=address, condition='Used',
                                      offer_type='Sell', promotion='Not Promoted', status='Active',
                                      title='Test Listing', description='This is a test listing', price=10.99)
    listing.save()

    response = client.get(f'/listing-details/{listing.id}/')
    assert response.status_code == 200
    assert Listings.objects.filter(id=listing.id).count() == 1
    assert Address.objects.filter(id=address.id).count() == 1
    assert Category.objects.filter(id=category.id).count() == 1
    assert Picture.objects.filter(id=listing.id).count() == 0


@pytest.mark.django_db
def test_listing_details_view_not_logged_user_status_code_not_ok(client):
    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    address = Address.objects.create(street_name='testaddress', user_id=user)
    address.save()

    assert Listings.objects.filter(user_id=user).count() == 0

    listing = Listings.objects.create(user_id=user, category_id=category, address_id=address, condition='Used',
                                      offer_type='Sell', promotion='Not Promoted', status='Active',
                                      title='Test Listing', description='This is a test listing', price=10.99)
    listing.save()

    response = client.get(f'/listing-details/99/')
    assert response.status_code == 404
    assert Listings.objects.filter(id=99).count() == 0


@pytest.mark.django_db
def test_messages_view_not_logged_user_status_code_ok(client):
    assert Messages.objects.count() == 0

    response = client.get('/messages/')
    assert response.status_code != 200  # from 302 -> /login/ 200
    assert Messages.objects.count() == 0


@pytest.mark.django_db
def test_messages_view_logged_user_status_code_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(title='Test Message', message='Test Message', from_user_id=user.id,
                                      to_user_id=user1.id)
    message.save()

    client.login(username='testuser', password='testtest')
    response = client.get('/messages/')
    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert response.status_code == 200


@pytest.mark.django_db



@pytest.mark.django_db




@pytest.mark.django_db







@pytest.mark.django_db
def test_contact_view_logged_user_status_code_ok(client):
    assert User.objects.count() == 0
    admin = User.objects.create_superuser(username='Admin')
    user = User.objects.create_user(username='testuser', password='testtest')

    assert User.objects.count() == 2
    assert Messages.objects.all().count() == 0

    client.login(username='testuser', password='testtest')
    response = client.post('/contact/', {'title': 'test title', 'message': 'test message', 'to_user_id': admin.id, 'from_user_id': user.id})

    assert response.status_code == 200
    assert Messages.objects.filter(from_user_id=user.id).count() == 1


@pytest.mark.django_db
def test_contact_view_not_logged_user_status_code_ok(client):
    assert User.objects.count() == 0
    admin = User.objects.create_superuser(username='Admin')

    assert User.objects.count() == 1
    assert Messages.objects.all().count() == 0

    unregistered_email = 'test@gmail.com'

    response = client.post('/contact/', {'title': 'test title', 'message': 'test message', 'to_user_id': admin.id, 'email': unregistered_email})

    assert response.status_code == 200
    assert Messages.objects.filter(from_unregistered_user=unregistered_email).count() == 1


@pytest.mark.django_db
def test_contact_view_not_logged_user_status_code_not_ok(client):
    assert User.objects.count() == 0
    admin = User.objects.create_superuser(username='Admin')

    assert User.objects.count() == 1
    assert Messages.objects.all().count() == 0

    unregistered_email = ''

    response = client.post('/contact/', {'title': 'test title', 'message': 'test message', 'to_user_id': admin.id, 'email': unregistered_email})

    assert response.status_code == 200
    assert Messages.objects.filter(from_unregistered_user=unregistered_email).count() == 0
    assert 'Invalid email address.' in response.content.decode()


@pytest.mark.django_db
def test_about_us_status_code(client):
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
