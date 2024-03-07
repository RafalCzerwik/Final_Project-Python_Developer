from django.shortcuts import render
from django.views import View


# Create your views here.

class IndexView(View):
    def get(self, request):
        return render(request, 'sell_it_app/index.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'sell_it_app/login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'sell_it_app/register.html')

    def post(self, request, *args, **kwargs):
        pass


class DashboardView(View):
    def get(self, request):
        return render(request, 'sell_it_app/dashboard.html')


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


