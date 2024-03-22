import datetime
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from sell_it_app.models import User, Category, Newsletter, Listings, Address, Picture, Messages, Avatars


# main page test


@pytest.mark.django_db
def test_index_page_status_code(client):
    """
    Test function to check the status code of the index page.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/')
    assert response.status_code == 200

# login page


@pytest.mark.django_db
def test_login_page_status_code(client):
    """
    Test function to check the status code of the login page.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/login/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_user_ok(client):
    """
    Test function to check if a user can login successfully.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    password = 'testtesttest'
    if len(password) >= 6:
        response = client.post('/login/', {'username': 'test', 'password': f'{password}'})
        assert response.status_code == 200


@pytest.mark.django_db
def test_login_user_invalid(client):
    """
    Test function to check if an invalid user login attempt returns the correct response.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post('/login/', {'username': 'test', f'password': 'a'})
    assert response.status_code == 200
    assert 'Invalid username or password.' in response.content.decode()


# logout

@pytest.mark.django_db
def test_logout_user_ok(client):
    """
    Test function to check if a user can logout successfully.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post('/logout/', {'username': 'test', 'password': 'passpass'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_register_user_ok(client):
    """
    Test function to check if a user can register successfully.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if registration with invalid data fails as expected.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if a user can be created successfully.

    Returns:
        None
    """

    user = User.objects.create_user(username='Rafal', email='test@gmail.com', password='secret_password')
    user.save()
    assert user.username == 'Rafal'
    assert user.email == 'test@gmail.com'
    assert User.objects.get(username=user.username) == user
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_create_user_invalid():
    """
    Test function to check if user creation fails with invalid data.

    Returns:
        None
    """

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
    """
    Test function to check if the admin panel is accessible for the admin user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if non-admin users cannot access the admin panel.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if accessing the dashboard page returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post('/dashboard/', {'username': 'test', 'password': 'testtesttest'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_dashboard_status_wrong_code(client):
    """
    Test function to check if accessing the dashboard page with wrong HTTP method returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/dashboard/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_category_status_code_ok(client):
    """
    Test function to check if accessing a valid category page returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    category = Category.objects.create(name='test', description='test')
    response = client.get("/category/1/")
    assert response.status_code == 200
    assert Category.objects.filter(name=category.name).count() == 1


@pytest.mark.django_db
def test_category_status_code_not_exists(client):
    """
    Test function to check if accessing a non-existing category page returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/category/1/')
    assert response.status_code == 404
    assert Category.objects.filter(pk=1).exists() is False


@pytest.mark.django_db
def test_profile_view_status_code(client):
    """
    Test function to check if accessing the profile page returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    user = User.objects.create_user(username='testuser', password='testtesttest')
    user.save()
    client.login(username='testuser', password='testtesttest')
    response = client.get('/profile/', {'username': 'test', 'password': 'testtesttest'})
    assert response.status_code == 200
    assert User.objects.filter(pk=user.pk).exists() is True


@pytest.mark.django_db
def test_profile_view_status_code_not_ok(client):
    """
    Test function to check if accessing the profile page without authentication returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/profile/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_update_password_view_status_code_ok(client):
    """
    Test function to check if updating password for an authenticated user returns the expected status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if updating password with invalid inputs returns the expected status code and error message.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if updating password without being logged in redirects to the login page.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post('/profile/update-password/')
    assert response.status_code == 302
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_update_profile_view_not_logged_status_code_ok(client):
    """
    Test function to check if accessing the update profile page without being logged in redirects to the login page.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/update-profile/')
    assert response.status_code == 302
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_update_profile_logged_user_status_code_ok_updated(client):
    """
    Test function to check if updating the profile of a logged-in user returns the expected status code and updates the user's profile.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if updating the profile of a logged-in user with invalid phone number does not update the profile.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to check if updating the avatar of a logged-in user returns the expected status code and updates the avatar.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='password')
    assert User.objects.count() == 1

    client.login(username='testuser', password='password')

    assert Avatars.objects.count() == 0

    image = open('sell_it_app/static/test/test_avatar.png', 'rb')
    uploaded_file = SimpleUploadedFile(name='test_avatar.png', content=image.read(), content_type='image/png')

    response = client.post('/update-profile/avatar/', {'avatar': uploaded_file}, follow=True)

    assert Avatars.objects.count() == 1
    assert response.status_code == 200
    assert Avatars.objects.get(user_id=user.id).avatar.url is not None

    update = Avatars.objects.filter(user_id=user.id).exists()

    if update:
        old_avatar = Avatars.objects.filter(user_id=user.id)
        old_avatar.delete()

        assert Avatars.objects.count() == 0

    image_new = open('sell_it_app/static/test/test_avatar.png', 'rb')
    uploaded_file = SimpleUploadedFile(name='test_avatar.png', content=image_new.read(), content_type='image/png')

    response1 = client.post('/update-profile/avatar/', {'avatar': uploaded_file}, follow=True)
    assert Avatars.objects.count() == 1
    assert response1.status_code == 200
    assert Avatars.objects.get(user_id=user.id).avatar.url is not None


@pytest.mark.django_db
def test_update_profile_avatar_logged_user_fail(client):
    """
    Test function to check if uploading a non-image file as an avatar fails.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='password')
    assert User.objects.count() == 1

    client.login(username='testuser', password='password')

    assert Avatars.objects.count() == 0

    image = open('sell_it_app/static/test/test_avatar.pdf', 'rb')
    uploaded_file = SimpleUploadedFile(name='test_avatar.pdf', content=image.read(), content_type='image/png')

    response = client.post('/update-profile/avatar/', {'avatar': uploaded_file}, follow=True)
    assert Avatars.objects.count() == 0
    assert response.status_code == 200
    assert not Avatars.objects.filter(user_id=user.id).exists()


@pytest.mark.django_db
def test_update_profile_avatar_view_not_logged_user_fail(client):
    """
    Test function to check if attempting to update avatar by a not logged-in user fails.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post('/update-profile/avatar/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_public_profile_view_status_code(client):
    """
    Test function to verify the status code of the public profile view.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    user = User.objects.create_user(username='testuser', password='testtesttest')
    user.save()
    client.login(username='testuser', password='testtesttest')
    response = client.get('/public_profile/')
    assert response.status_code == 404
    assert User.objects.filter(pk=user.pk).exists() is True


@pytest.mark.django_db
def test_public_profile_view_status_code_not_ok(client):
    """
    Test function to verify the status code of the public profile view when the user is not logged in.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/public_profile/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_search_view_logged_user_status_code_ok(client):
    """
    Test function to verify the status code of the search view for a logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    user = User.objects.create_user(username='testuser', password='testtesttest')
    user.save()
    client.login(username='testuser', password='testtesttest')
    search_query = 'test'
    response = client.get(f'/search/?search_query={search_query}')
    assert response.status_code == 200
    assert Listings.objects.filter(title__icontains=search_query).order_by('title').count() == 0


@pytest.mark.django_db
def test_search_view_not_logged_user_status_code_ok(client):
    """
    Test function to verify the status code of the search view for a not logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    search_query = 'test'
    response = client.post(f'/search/?search_query={search_query}')
    assert response.status_code != 200
    assert Listings.objects.filter(title__icontains=search_query).order_by('title').count() == 0


@pytest.mark.django_db
def test_listings_view_logged_user_status_code_ok(client):
    """
    Test function to verify the status code of the listings view for a logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    client.login(username='testuser', password='testtesttesttest')
    response = client.get('/listings/')
    assert response.status_code == 200
    assert Listings.objects.filter(user_id=user).count() == 0


@pytest.mark.django_db
def test_listings_view_not_logged_user_status_code_ok(client):
    """
    Test function to verify the status code of the listings view for a not logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.get('/listings/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_listing_map_view_logged_user_status_code_ok(client):
    """
    Test function to verify the status code of the listing map view for a logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0

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
    """
    Test function to verify the status code of the listing details view for a logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to verify the status code of the listing details view for a not logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
    """
    Test function to verify the status code of the listing details view for a not logged-in user when the listing ID does not exist.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

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
def test_add_listing_view_logged_user_status_code_ok(client):
    """
    Test function to verify the status code and functionality of adding a listing by a logged-in user.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0
    assert Picture.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    client.login(username='testuser', password='testtesttesttest')

    response = client.get('/add-listing/')
    assert response.status_code == 200

    image1 = open('sell_it_app/static/test/test_avatar1.png', 'rb')
    image2 = open('sell_it_app/static/test/test_avatar2.png', 'rb')
    uploaded_file1 = SimpleUploadedFile(name='test_avatar1.png', content=image1.read(), content_type='image/png')
    uploaded_file2 = SimpleUploadedFile(name='test_avatar2.png', content=image2.read(), content_type='image/png')
    multiple_images = [uploaded_file1, uploaded_file2]

    post_data = {
        'user_id': user.pk,
        'category_id': category.pk,
        'condition': 'New',
        'offer_type': 'Sell',
        'image': multiple_images,
        'street_name': 'Test address',
        'postal_code': '12345',
        'country': 'country',
        'city': 'city',
        'title': 'Test title',
        'description': 'This is a test listing',
        'price': 100
    }

    response = client.post('/add-listing/', post_data)

    assert response.status_code == 302
    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1
    assert Picture.objects.count() == 2

@pytest.mark.django_db
def test_add_listing_view_logged_user_status_code_not_ok(client):
    """
    Test function to verify the status code and functionality of adding a listing by a logged-in user with invalid data.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0
    assert Picture.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    client.login(username='testuser', password='testtesttesttest')

    response = client.get('/add-listing/')
    assert response.status_code == 200

    image1 = open('sell_it_app/static/test/test_avatar1.png', 'rb')
    image2 = open('sell_it_app/static/test/test_avatar2.png', 'rb')
    uploaded_file1 = SimpleUploadedFile(name='test_avatar1.png', content=image1.read(), content_type='image/png')
    uploaded_file2 = SimpleUploadedFile(name='test_avatar2.png', content=image2.read(), content_type='image/png')
    image1.close()
    image2.close()

    image_dict = MultiValueDict({'image': [uploaded_file1, uploaded_file2]})

    post_data = {
        'user_id': user.pk,
        'category_id': category.pk,
        'image': image_dict,
        'street_name': 'Test address',
        'postal_code': '12345',
        'country': 'country',
        'city': 'city',
        'price': 100
    }
    try:
        response = client.post('/add-listing/', post_data, **image_dict)
    except IntegrityError:
        pass

        assert response.status_code != 302
        assert Listings.objects.count() == 0
        assert Address.objects.count() == 0
        assert Picture.objects.count() == 0


@pytest.mark.django_db
def test_add_listing_unregistered_fail(client):
    """
    Test function to verify that unregistered users cannot access the add listing page.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post('/add-listing/')
    assert response.status_code != 200


@pytest.mark.django_db
def test_edit_listing_view_status_code_ok(client):
    """
    Test function to verify that the edit listing view returns a status code of 302 (Redirect) upon successful editing.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    client.login(username='testuser', password='testtesttesttest')

    address = Address.objects.create(
        user_id=user,
        street_name='test',
        street_name_secondary='test',
        postal_code='1234',
        city='test',
        country='test'
    )

    listing = Listings.objects.create(
            user_id=user,
            category_id=category,
            address_id=address,
            condition='New',
            offer_type='Sell',
            title='Test title',
            description='This is a test listing',
            price=100,
    )

    response = client.post(f'/edit-listing/{listing.id}/', {
        'title': 'new title',
        'description': 'new description',
        'condition': listing.condition,
        'offer_type': listing.offer_type,
        'price': listing.price,
        'category_id': listing.category_id.id,
        'address_id': listing.address_id.id,
        'user_id': user.id,
        'street_name': address.street_name,
        'city': address.city,
        'postal_code': address.postal_code,
        'country': address.country,
    })

    listing.refresh_from_db()
    assert response.status_code == 302
    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1
    assert listing.title == 'new title'
    assert listing.description == 'new description'


@pytest.mark.django_db
def test_edit_listing_view_status_code_not_ok(client):
    """
    Test function to verify that the edit listing view returns a status code other than 302 (Redirect)
    when the request is incomplete or invalid.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    client.login(username='testuser', password='testtesttesttest')

    address = Address.objects.create(
        user_id=user,
        street_name='test',
        street_name_secondary='test',
        postal_code='1234',
        city='test',
        country='test'
    )

    listing = Listings.objects.create(
            user_id=user,
            category_id=category,
            address_id=address,
            condition='New',
            offer_type='Sell',
            title='Test title',
            description='This is a test listing',
            price=100,
    )

    response = client.post(f'/edit-listing/{listing.id}/')

    assert response.status_code != 302
    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1


@pytest.mark.django_db
def test_edit_listing_picture_success(client):
    """
    Test function to verify that adding pictures to a listing is successful.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0
    assert Picture.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()
    address = Address.objects.create(
        user_id=user,
        street_name='Test address',
        street_name_secondary='Test address',
        postal_code='12345',
        country='country',
        city='city',
    )

    client.login(username='testuser', password='testtesttesttest')

    image1 = open('sell_it_app/static/test/test_avatar1.png', 'rb')
    image2 = open('sell_it_app/static/test/test_avatar2.png', 'rb')
    uploaded_file1 = SimpleUploadedFile(name='test_avatar1.png', content=image1.read(), content_type='image/png')
    uploaded_file2 = SimpleUploadedFile(name='test_avatar2.png', content=image2.read(), content_type='image/png')
    multiple_images = [uploaded_file1, uploaded_file2]
    image1.close()
    image2.close()

    listing = Listings.objects.create(
        user_id=user,
        category_id=category,
        address_id=address,
        condition='New',
        offer_type='Sell',
        title='Test title',
        description='This is a test listing',
        price=100,
    )
    for upload in multiple_images:
        Picture.objects.create(user_id=user, listing_id=listing.id, image=upload)


    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1
    assert Picture.objects.count() == 2

    image3 = open('sell_it_app/static/test/test_avatar3.png', 'rb')
    image4 = open('sell_it_app/static/test/test_avatar4.png', 'rb')
    uploaded_file1 = SimpleUploadedFile(name='test_avatar3.png', content=image3.read(), content_type='image/png')
    uploaded_file2 = SimpleUploadedFile(name='test_avatar4.png', content=image4.read(), content_type='image/png')
    new_multiple_images = [uploaded_file1, uploaded_file2]
    image3.close()
    image4.close()

    response = client.post(f'/edit-listing/{listing.id}/picture/', {'user_id': user, 'listing_id': listing.id, 'image': new_multiple_images})

    assert response.status_code == 302
    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1
    assert Picture.objects.count() == 4


@pytest.mark.django_db
def test_edit_listing_picture_fail(client):
    """
    Test function to verify that adding pictures to a non-existent listing fails.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post(f'/edit-listing/99/picture/')
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_listing_picture_success(client):
    """
    Test function to verify successful deletion of a listing picture.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0
    assert Picture.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()
    address = Address.objects.create(
        user_id=user,
        street_name='Test address',
        street_name_secondary='Test address',
        postal_code='12345',
        country='country',
        city='city',
    )

    client.login(username='testuser', password='testtesttesttest')

    image1 = open('sell_it_app/static/test/test_avatar1.png', 'rb')
    image2 = open('sell_it_app/static/test/test_avatar2.png', 'rb')
    image3 = open('sell_it_app/static/test/test_avatar3.png', 'rb')
    uploaded_file1 = SimpleUploadedFile(name='test_avatar1.png', content=image1.read(), content_type='image/png')
    uploaded_file2 = SimpleUploadedFile(name='test_avatar2.png', content=image2.read(), content_type='image/png')
    uploaded_file3 = SimpleUploadedFile(name='test_avatar3.png', content=image3.read(), content_type='image/png')
    multiple_images = [uploaded_file1, uploaded_file2, uploaded_file3]
    image1.close()
    image2.close()
    image3.close()

    listing = Listings.objects.create(
        user_id=user,
        category_id=category,
        address_id=address,
        condition='New',
        offer_type='Sell',
        title='Test title',
        description='This is a test listing',
        price=100,
    )
    pictures = []
    for upload in multiple_images:
        picture = Picture.objects.create(user_id=user, listing_id=listing.id, image=upload)
        pictures.append(picture)

    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1
    assert Picture.objects.count() == 3

    picture_delete = pictures[2]

    response = client.post(f'/delete-listing-picture/{listing.id}/{picture_delete.id}/')

    assert response.status_code == 302
    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1
    assert Picture.objects.count() == 2


@pytest.mark.django_db
def test_delete_listing_picture_fail(client):
    """
    Test function to verify failure when attempting to delete a listing picture with invalid listing or picture IDs.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    response = client.post(f'/delete-listing-picture/99/1/')
    assert response.status_code == 302


@pytest.mark.django_db
def test_update_listing_status_view_success(client):
    """
    Test function to verify successful update of listing status.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    client.login(username='testuser', password='testtesttesttest')

    address = Address.objects.create(
        user_id=user,
        street_name='test',
        street_name_secondary='test',
        postal_code='1234',
        city='test',
        country='test'
    )

    listing = Listings.objects.create(
        user_id=user,
        category_id=category,
        address_id=address,
        condition='New',
        offer_type='Sell',
        title='Test title',
        description='This is a test listing',
        price=100,
        status='Active',
    )

    assert listing.status == 'Active'
    assert User.objects.count() == 1
    assert Category.objects.count() == 1
    assert Address.objects.count() == 1
    assert Listings.objects.count() == 1

    response = client.post(f'/listing/update-status/{listing.id}/', {'status': 'Inactive'})

    listing.refresh_from_db()
    assert listing.status == 'Inactive'
    assert response.status_code == 302
    assert Listings.objects.count() == 1
    assert Address.objects.count() == 1


@pytest.mark.django_db
def test_update_listing_status_view_fail(client):
    """
    Test function to verify failure to update listing status due to non-existent listing ID.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    user = User.objects.create_user(username='testuser', password='testtesttesttest')
    client.login(username='testuser', password='testtesttesttest')

    response = client.post(f'/listing/update-status/99/', {'status': 'Inactive'})

    assert response.status_code == 404
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_delete_listing_view_status_code_ok(client):
    """
    Test function to verify successful deletion of a listing.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    assert User.objects.count() == 0
    assert Category.objects.count() == 0
    assert Address.objects.count() == 0
    assert Listings.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtesttesttest')

    category = Category.objects.create(name='testcategory')
    category.save()

    client.login(username='testuser', password='testtesttesttest')

    address = Address.objects.create(
        user_id=user,
        street_name='test',
        street_name_secondary='test',
        postal_code='1234',
        city='test',
        country='test'
    )

    listing = Listings.objects.create(
        user_id=user,
        category_id=category,
        address_id=address,
        condition='New',
        offer_type='Sell',
        title='Test title',
        description='This is a test listing',
        price=100,
    )
    assert User.objects.count() == 1
    assert Category.objects.count() == 1
    assert Address.objects.count() == 1
    assert Listings.objects.count() == 1

    response = client.post(f'/delete-listing/{listing.id}/')

    assert response.status_code == 302
    assert Listings.objects.count() == 0
    assert Address.objects.count() == 1


@pytest.mark.django_db
def test_delete_listing_view_status_code_not_ok(client):
    """
    Test function to verify deletion of a non-existent listing returns a 404 status code.

    Args:
        client (Client): Django test client.

    Returns:
        None
    """

    user = User.objects.create_user(username='testuser', password='testtesttesttest')
    client.login(username='testuser', password='testtesttesttest')

    response = client.post('/delete-listing/99/')

    assert response.status_code == 404
    assert User.objects.count() == 1

@pytest.mark.django_db
def test_update_message_status_code_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(title='Test Message', message='Test Message', from_user_id=user.id,
                                      to_user_id=user1.id, status='Unread')
    message.save()

    assert message.status == 'Unread'

    client.login(username='testuser', password='testtest')

    response = client.post(f'/message/update-status/{message.id}/', {'status': 'Read'})

    message.refresh_from_db()
    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert response.status_code == 302
    assert message.status == 'Read'


@pytest.mark.django_db
def test_update_message_status_code_not_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')
    user2 = User.objects.create_user(username='testuser2', password='testtest2')

    message = Messages.objects.create(title='Test Message', message='Test Message', from_user_id=user.id,
                                      to_user_id=user1.id, status='Unread')
    message.save()

    assert message.status == 'Unread'

    client.login(username='testuser2', password='testtest2')

    response = client.post(f'/message/update-status/{message.id}/')

    message.refresh_from_db()
    assert Messages.objects.count() == 1
    assert User.objects.count() == 3
    assert response.status_code == 403
    assert message.status == 'Unread'

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
def test_messages_delete_view_status_code_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(
        title='Test Message',
        message='Test Message',
        from_user=user,
        to_user=user1,
    )
    message.save()

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2

    client.login(username='testuser', password='testtest')
    response = client.post(f'/message/delete/{message.pk}/')

    assert Messages.objects.count() == 0
    assert User.objects.count() == 2
    assert response.status_code == 302


@pytest.mark.django_db
def test_messages_delete_view_status_code_not_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(
        title='Test Message',
        message='Test Message',
        from_user=user,
        to_user=user1,
    )
    message.save()

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2

    client.login(username='testuser', password='testtest')
    response = client.post(f'/message/delete/99/')

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert response.status_code != 302


@pytest.mark.django_db
def test_send_messages_view_status_code_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(
        title='Test Message',
        message='Test Message',
        from_user=user,
        to_user=user1,
    )
    message.save()

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2

    client.login(username='testuser1', password='testtest1')
    response = client.post(f'/send-message/{message.id}/', {
        'from_user': user1,
        'to_user': user,
        'title': message.title,
        'message': 'test return message'
    })

    assert Messages.objects.count() == 2
    assert User.objects.count() == 2
    assert response.status_code == 200


@pytest.mark.django_db
def test_send_messages_view_status_code_not_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(
        title='Test Message',
        message='Test Message',
        from_user=user,
        to_user=user1,
    )
    message.save()

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2

    client.login(username='testuser1', password='testtest1')
    response = client.post(f'/send-message/99/', {
        'from_user': user1,
        'to_user': user,
        'title': message.title,
        'message': 'test return message'
    })

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert response.status_code != 200


@pytest.mark.django_db
def test_show_messages_view_status_code_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(
        title='Test Message',
        message='Test Message',
        from_user=user,
        to_user=user1,
    )
    message.save()

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2

    client.login(username='testuser1', password='testtest1')
    response = client.get(f'/show-message/{message.id}/')

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert response.status_code == 200


@pytest.mark.django_db
def test_show_messages_view_status_code_not_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    message = Messages.objects.create(
        title='Test Message',
        message='Test Message',
        from_user=user,
        to_user=user1,
    )
    message.save()

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2

    client.login(username='testuser1', password='testtest1')
    response = client.get(f'/show-message/99/')

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert response.status_code != 200

@pytest.mark.django_db
def test_send_new_message_view_status_code_ok(client):
    assert Messages.objects.count() == 0
    assert User.objects.count() == 0
    assert Address.objects.count() == 0
    assert Category.objects.count() == 0
    assert Listings.objects.count() == 0

    user = User.objects.create_user(username='testuser', password='testtest')
    user1 = User.objects.create_user(username='testuser1', password='testtest1')

    category = Category.objects.create(name='Test')
    address = Address.objects.create(user_id=user, street_name='Test Street', street_name_secondary='test', country='test country', postal_code="1234", city='Test')

    listing = Listings.objects.create(
        user_id=user,
        category_id=category,
        address_id=address,
        condition='Used',
        offer_type='Sell',
        promotion='Not Promoted',
        description='test',
        price=100
    )

    client.login(username='testuser1', password='testtest1')

    response = client.post(f'/send-new-message/{listing.id}/', {
        'title': listing.title,
        'message': 'test message text',
        'from_user': user1,
        'to_user': user,
    })

    assert Messages.objects.count() == 1
    assert User.objects.count() == 2
    assert Address.objects.count() == 1
    assert Category.objects.count() == 1
    assert Listings.objects.count() == 1
    assert response.status_code == 302


@pytest.mark.django_db
def test_send_new_message_view_status_code_not_ok(client):
    response = client.post(f'/send-new-message/99/')

    assert Messages.objects.count() == 0
    assert User.objects.count() == 0
    assert Address.objects.count() == 0
    assert Category.objects.count() == 0
    assert Listings.objects.count() == 0
    assert response.status_code == 302


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
def test_newsletter_ok(client):
    response = client.get(reverse('newsletter'))
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
