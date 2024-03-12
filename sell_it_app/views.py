import random

from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from sell_it_app.forms import AvatarForm
from sell_it_app.models import Messages, Newsletter, Avatars, Listings, Category

User = get_user_model()


class IndexView(View):
    def get(self, request):
        promoted_listings = list(Listings.objects.filter(promotion='Promoted').order_by('-add_date'))
        random.shuffle(promoted_listings)
        carousel = promoted_listings[:3]

        last_added = Listings.objects.filter(promotion='Promoted').order_by('-add_date')[:6]

        ctx = {
            'promoted_listings': promoted_listings,
            'last_added': last_added,
            'carousel': carousel,
        }
        return render(request, 'sell_it_app/index.html', ctx)


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


class LogOutView(LoginRequiredMixin, View):
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


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        avatar = Avatars.objects.filter(user_id=request.user).last()
        return render(request, 'sell_it_app/dashboard.html', {'avatar': avatar})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        avatar = Avatars.objects.filter(user_id=request.user).last()
        form = AvatarForm()
        return render(request, 'sell_it_app/profile.html', {'avatar': avatar, 'form': form})

    def post(self, request):
        form = AvatarForm(request.POST, request.FILES)
        avatar = Avatars.objects.filter(user_id=request.user).first()
        user = request.user
        if form.is_valid():
            avatar = form.save(commit=False)
            avatar.user_id = user
            avatar.save()
            return redirect('profile')
        else:
            form = AvatarForm()
        return render(request, 'sell_it_app/profile.html', {'form': form, 'avatar': avatar})


class PublicProfileView(View):
    def get(self, request):
        return render(request, 'sell_it_app/public_profile.html')


class SearchView(View):
    def get(self, request):
        search_query = request.GET.get('search_query')
        searching = Listings.objects.filter(title__icontains=search_query)
        ctx = {'searching': searching}
        return render(request, 'sell_it_app/search_results.html', ctx)


class MyListingsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'sell_it_app/my_listings.html')


class MessagesView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            id = user.id
            messages = Messages.objects.filter(to_user=id).order_by('-id')
            user_messages = Messages.objects.filter(to_user_id=id).count()
            user_unread_messages = Messages.objects.filter(to_user_id=id).filter(status='Unread').count()
            user_read_messages = Messages.objects.filter(to_user_id=id).filter(status='Read').count()
            user_sent_messages = Messages.objects.filter(from_user_id=id).count()

            ctx = {
                'user_messages': user_messages,
                'user_unread_messages': user_unread_messages,
                'user_read_messages': user_read_messages,
                'user_sent_messages': user_sent_messages,
                'messages': messages,
            }

            return render(request, 'sell_it_app/messages.html', ctx)


class MessageStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, message_id):
        message = get_object_or_404(Messages, id=message_id)
        if message.status == 'Unread':
            message.status = 'Read'
            message.save()
            return redirect('messages')
        if message.status == 'Read':
            message.status = 'Unread'
            message.save()
            return redirect('messages')


class MessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, message_id):
        message = get_object_or_404(Messages, id=message_id)

        if message:
            message.delete()
            return redirect('messages')


class ShowMessageView(LoginRequiredMixin, View):
    def get(self, request, message_id):
        message = get_object_or_404(Messages, pk=message_id)

        if message.from_unregistered_user:
            ctx = {
                'title': message.title,
                'message': message.message,
                'sender': message.from_unregistered_user,
                'current_message': message,
            }

            return render(request, 'sell_it_app/message.html', ctx)
        else:
            ctx = {
                'title': message.title,
                'message': message.message,
                'sender': message.from_user,
                'current_message': message,
            }

            return render(request, 'sell_it_app/message.html', ctx)


class SendMessageView(LoginRequiredMixin, View):
    def get(self, request, message_id):
        current_message = get_object_or_404(Messages, pk=message_id)
        return render(request, 'sell_it_app/message.html', {'current_message': current_message})

    def post(self, request, message_id):
        current_message = get_object_or_404(Messages, pk=message_id)
        # title = request.POST.get('title')
        title = f"RE: {current_message.title}"
        message_text = request.POST.get('message')
        user = request.user

        message_from_user = current_message.message
        message_sender = current_message.from_user
        message_sender_unregistered = current_message.from_unregistered_user
        message_title = current_message.title

        if current_message.from_user:
            send_message = Messages.objects.create(
                title=title,
                message=message_text,
                to_user=current_message.from_user,
                from_user=user,
            )
            send_message.save()
            success_message = 'Message sent successfully'

            ctx = {
                'success_message': success_message,
                'current_message': current_message,
                'message': message_from_user,
                'sender': message_sender,
                'title': message_title,
            }

            return render(request, 'sell_it_app/message.html', ctx)

        elif current_message.from_unregistered_user:
            error_message = "You can't send message to unregistered user!"

            ctx = {
                'error_message': error_message,
                'current_message': current_message,
                'message': message_from_user,
                'sender': message_sender_unregistered,
                'title': message_title,
            }
            return render(request, 'sell_it_app/message.html', ctx)


class AddListingView(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()

        ctx = {
            'categories': categories,
        }
        return render(request, 'sell_it_app/add_listing.html', ctx)


class ListingView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'sell_it_app/listing.html')


class MyAddressView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'sell_it_app/my_address.html')


class PaymentsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'sell_it_app/payments.html')


class FavouritesView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'sell_it_app/favourites.html')


class SavedSearchesView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'sell_it_app/saved_searches.html')


class AboutUsView(View):
    def get(self, request):
        return render(request, 'sell_it_app/about_us.html')


class ContactUsView(View):
    def get(self, request):
        return render(request, 'sell_it_app/contact_us.html')

    def post(self, request):
        title = request.POST.get('title')
        message = request.POST.get('message')

        unregistered_email = request.POST.get('email')

        user = request.user
        admin = User.objects.get(username='Admin')

        if user.is_authenticated:
            sender = user.id

            if user.username == admin.username:
                error_message = "You can't send an email to yourself!"
                return render(request, 'sell_it_app/contact_us.html', {'error_message': error_message})

            else:
                email_to_send = Messages.objects.create(
                    title=title,
                    message=message,
                    from_user_id=sender,
                    to_user_id=admin.id,
                )
                email_to_send.save()

                success_message = "Message is successfully sent!"
                return render(request, 'sell_it_app/contact_us.html', {'success_message': success_message})

        else:
            if "@" not in unregistered_email or "." not in unregistered_email:
                error_message = 'Invalid email address.'
                return render(request, 'sell_it_app/contact_us.html', {'error_message': error_message})

            else:
                email_to_send = Messages.objects.create(
                    title=title,
                    message=message,
                    to_user_id=admin.id,
                    from_unregistered_user=unregistered_email,
                )
                email_to_send.save()

                success_message = "Message is successfully sent!"
                return render(request, 'sell_it_app/contact_us.html', {'success_message': success_message})


class NewsletterView(View):
    def get(self, request):
        return render(request, 'sell_it_app/newsletter.html')

    def post(self, request):
        email = request.POST.get('email')
        registered_email = Newsletter.objects.filter(email=email).last()

        if registered_email:
            messages.error(request, 'Email already registered!')
            return redirect('newsletter')
        else:
            subscribe = Newsletter.objects.create(email=email)

        return redirect('newsletter')

