from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View


User = get_user_model()


class IndexView(View):
    def get(self, request):
        return render(request, 'sell_it_app/index.html')


class LoginView(View):
    """
    This class-based view handles user login.

    When a GET request is received, it serves the login page. For a POST request, it authenticates the provided
    credentials. If authentication is successful, it logs in the user and redirects them to the dashboard.
    Otherwise, it re-renders the login page with an error message.
    """

    def get(self, request):
        return render(request, 'sell_it_app/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'sell_it_app/login.html', {'error_message': error_message})


class LogOutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')


class RegisterView(View):
    def get(self, request):
        return render(request, 'sell_it_app/register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password_confirm')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('dob')

        ctx = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'password': password,
            'confirm_password': confirm_password,
            'email': email,
            'date_of_birt': date_of_birth,
        }

        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists.'
            return render(request, 'sell_it_app/register.html', {'error_message': error_message})

        if gender not in dict(User.GENDER_CHOICES):
            error_message = 'Invalid gender choice.'
            return render(request, 'sell_it_app/register.html', {'error_message': error_message})

        if len(password) < 6:
            error_message = 'Password must be at least 6 characters long.'
            return render(request, 'sell_it_app/register.html', {'error_message': error_message})
        elif password != confirm_password:
            error_message = 'Passwords do not match.'
            return render(request, 'sell_it_app/register.html', {'error_message': error_message})
        else:
            new_user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                email=email,
                password=password,
                date_of_birth=date_of_birth,
            )
            new_user.save()
            return redirect('login')


class DashboardView(View):
    def get(self, request):
        return render(request, 'sell_it_app/dashboard.html')


class ProfileView(View):
    def get(self, request):
        return render(request, 'sell_it_app/profile.html')


class PublicProfileView(View):
    def get(self, request):
        return render(request, 'sell_it_app/public_profile.html')


class TestView(View):
    def get(self, request):
        return render(request, 'sell_it_app/test.html')


class SearchView(View):
    def get(self, request):
        return render(request, 'sell_it_app/search_results.html')


class MyListingsView(View):
    def get(self, request):
        return render(request, 'sell_it_app/my_listings.html')


class MessagesView(View):
    def get(self, request):
        return render(request, 'sell_it_app/messages.html')


class SendMessageView(View):
    def get(self, request):
        return render(request, 'sell_it_app/send_message.html')


class AddListingView(View):
    def get(self, request):
        return render(request, 'sell_it_app/add_listing.html')


class ListingView(View):
    def get(self, request):
        return render(request, 'sell_it_app/listing.html')


class MyAddressView(View):
    def get(self, request):
        return render(request, 'sell_it_app/my_address.html')


class PaymentsView(View):
    def get(self, request):
        return render(request, 'sell_it_app/payments.html')


class FavouritesView(View):
    def get(self, request):
        return render(request, 'sell_it_app/favourites.html')


class SavedSearchesView(View):
    def get(self, request):
        return render(request, 'sell_it_app/saved_searches.html')


class AboutUsView(View):
    def get(self, request):
        return render(request, 'sell_it_app/about_us.html')


class ContactUsView(View):
    def get(self, request):
        return render(request, 'sell_it_app/contact_us.html')

