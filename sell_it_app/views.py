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
        pass


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

