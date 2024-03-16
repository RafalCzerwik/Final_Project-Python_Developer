import random

from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from sell_it_app.forms import AvatarForm, ListingsForm, AddressesForm, PictureForm, ProfileForm, PasswordForm
from sell_it_app.models import Messages, Newsletter, Avatars, Listings, Category, Picture, Address

User = get_user_model()


class IndexView(View):
    def get(self, request):
        #promoted_listings = list(Listings.objects.filter(promotion='Promoted').order_by('-add_date'))
        promoted_listings = list(Listings.objects.filter(promotion='Promoted').order_by('-add_date'))
        random.shuffle(promoted_listings)
        carousel = promoted_listings[:3]
        last_added = Listings.objects.all().order_by('-add_date')[:6]

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


class CategoryView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        listings = Listings.objects.filter(category_id=category).order_by('-add_date')

        paginator = Paginator(listings, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        ctx = {
            'category': category,
            'listings': page_obj,
        }
        return render(request, 'sell_it_app/category.html', ctx)


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        avatar = Avatars.objects.filter(user_id=request.user).last()
        return render(request, 'sell_it_app/dashboard.html', {'avatar': avatar})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        avatar = Avatars.objects.filter(user_id=request.user).last()
        form = AvatarForm()
        return render(request, 'sell_it_app/profile.html', {'avatar': avatar, 'form': form})


class UpdateProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        form = ProfileForm(instance=user)
        return render(request, 'sell_it_app/profile.html', {'user': user, 'form': form})

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            print(form.errors)
            messages.error(request, 'Error! Check your inputs!')

        return render(request, 'sell_it_app/profile.html', {'form': form, 'user': user})


class UpdatePassword(LoginRequiredMixin, View):
    def post(self, request):
        form = PasswordForm(request.POST)
        avatar = Avatars.objects.filter(user_id=request.user).first()
        user = request.user
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()

            messages.success(request, 'Password updated successfully!')
            update_session_auth_hash(request, user)
            return redirect('profile')

        return render(request, 'sell_it_app/profile.html', {'form': form, 'user': user, 'avatar': avatar})


class UpdateProfileAvatarView(LoginRequiredMixin, View):
    def post(self, request):
        form = AvatarForm(request.POST, request.FILES)
        avatar = Avatars.objects.filter(user_id=request.user).first()
        user = request.user
        if form.is_valid():
            if avatar:
                existing_avatar = Avatars.objects.get(user_id=request.user)
                existing_avatar.delete()
            avatar = form.save(commit=False)
            avatar.user_id = user
            avatar.save()
            messages.success(request, 'Avatar updated successfully!')
            return redirect('profile')
        else:
            form = AvatarForm()
        return render(request, 'sell_it_app/profile.html', {'form': form, 'avatar': avatar})


class PublicProfileView(View):
    def get(self, request):
        return render(request, 'sell_it_app/public_profile.html')


class SearchView(View):
    def get(self, request):
        query = request.GET.get('search_query')
        searching = Listings.objects.filter(title__icontains=query).order_by('title')

        if not searching.exists():
            messages.error(request, 'No results found.')

        paginator = Paginator(searching, 1)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        ctx = {
            'searching': searching,
            'page_obj': page_obj,
        }
        return render(request, 'sell_it_app/search_results.html', ctx)


class MyListingsView(LoginRequiredMixin, View):
    def get(self, request):
        all_listings = Listings.objects.filter(user_id=request.user.id).count()
        listings = Listings.objects.filter(user_id=request.user.id).order_by('-add_date')
        active_listings = Listings.objects.filter(user_id=request.user.id).filter(status='Active').count()
        inactive_listings = Listings.objects.filter(user_id=request.user.id).filter(status='Inactive').count()

        listings_type = request.GET.get('listings_type', 'All')
        if listings_type == 'All':
            listings = Listings.objects.filter(user_id=request.user.id).order_by('-add_date')
        elif listings_type == 'Active':
            listings = Listings.objects.filter(user_id=request.user.id).filter(status='Active').order_by('-add_date')
        elif listings_type == 'Inactive':
            listings = Listings.objects.filter(user_id=request.user.id).filter(status='Inactive').order_by('-add_date')

        paginator = Paginator(listings, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'sell_it_app/my_listings.html', {
            'all_listings': all_listings,
            'active_listings': active_listings,
            'inactive_listings': inactive_listings,
            'listings': page_obj,
            'listings_type': listings_type,
        })


class ListingView(View):
    def get(self, request, listing_id):
        user = request.user
        if user.is_authenticated:
            listing = get_object_or_404(Listings, pk=listing_id)
            avatar = Avatars.objects.filter(user_id=request.user).last()
            pictures = Picture.objects.filter(listing=listing_id)
            return render(request, 'sell_it_app/listing.html', {'listing': listing, 'avatar': avatar, 'pictures': pictures})
        else:
            listing = get_object_or_404(Listings, pk=listing_id)
            picture = Picture.objects.filter(listing=listing_id)
            return render(request, 'sell_it_app/listing.html', {'listing': listing, 'picture': picture})


class AddListingView(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()

        ctx = {
            'categories': categories,
        }
        return render(request, 'sell_it_app/add_listing.html', ctx)

    def post(self, request):
        picture_form = PictureForm(request.POST, request.FILES)
        address_form = AddressesForm(request.POST)
        listing_form = ListingsForm(request.POST)

        ctx = {}

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user_id = request.user
            # address.listing_id = listing
            address.save()
            ctx['address'] = address
        else:
            print("Address form errors:", address_form.errors)

        listing = None

        if listing_form.is_valid():
            listing = listing_form.save(commit=False)
            listing.user_id = request.user
            listing.address_id = address
            listing.save()
            ctx['listing'] = listing
        else:
            print("Listing form errors:", listing_form.errors)

        if picture_form.is_valid():
            pictures = []
            pictures_instance = picture_form.save(commit=False)
            for file in request.FILES.getlist('image'):
                picture = Picture(user_id=request.user, image=file, listing=listing)
                picture.save()
                pictures.append(picture)
            ctx['pictures'] = pictures
        else:
            print("Picture form errors:", picture_form.errors)

        if listing_form.is_valid() and picture_form.is_valid() and address_form.is_valid():
            # return render(request, 'sell_it_app/listing.html', ctx)
            return redirect('listing-details', listing_id=listing.id)
        else:
            error_message = 'Error! Please check and try again!'
            return render(request, 'sell_it_app/add_listing.html', {'error_message': error_message})


class EditListingView(LoginRequiredMixin, View):
    def get(self, request, listing_id):
        listing = get_object_or_404(Listings, pk=listing_id)
        categories = Category.objects.all()
        address = Address.objects.get(id=listing.address_id.id)
        pictures = Picture.objects.filter(listing=listing_id)

        return render(request, 'sell_it_app/edit_listing.html', {
            'listing': listing,
            'categories': categories,
            'address': address,
            'pictures': pictures,
        })

    def post(self, request, listing_id):
        listing = get_object_or_404(Listings, pk=listing_id)
        listing_form = ListingsForm(request.POST, instance=listing)
        address_form = AddressesForm(request.POST, instance=listing.address_id)

        if listing_form.is_valid() and address_form.is_valid():
            address = address_form.save(commit=False)
            address.user_id = request.user
            address.save()

            listing = listing_form.save(commit=False)
            listing.user = request.user
            listing.address_id = address
            listing.save()

            messages.success(request, 'Listing details updated successfully!')
            return redirect('edit-listing', listing_id=listing.id)

        else:
            print(listing_form.errors)
            print(address_form.errors)
            print(request.user)
            return render(request, 'sell_it_app/edit_listing.html', {'listing': listing})


class EditListingPictureView(LoginRequiredMixin, View):
    def get(self, request, listing_id):
        listing = get_object_or_404(Listings, pk=listing_id)
        return render(request, 'sell_it_app/edit_listing.html', {'listing': listing})

    def post(self, request, listing_id):
        listing = get_object_or_404(Listings, pk=listing_id)
        picture_form = PictureForm(request.POST, request.FILES)

        if picture_form.is_valid():
            pictures = []
            existing_pictures = Picture.objects.filter(listing_id=listing.id, user_id=request.user)
            existing_pictures.delete()
            picture = picture_form.save(commit=False)
            for file in request.FILES.getlist('image'):
                picture = Picture(user_id=request.user, image=file, listing=listing)
                picture.save()
                pictures.append(picture)
            picture.listing_id = listing.id
            picture.user_id = request.user
            picture.save()

            messages.success(request, 'Picture uploaded successfully!')
            return redirect('edit-listing', listing.id)

        return render(request, 'sell_it_app/edit_listing.html', {'listing': listing})


class DeleteListingPicture(LoginRequiredMixin, View):
    def post(self, request, listing_id, picture_id):
        listing = get_object_or_404(Listings, pk=listing_id)
        picture = Picture.objects.get(pk=picture_id)

        if picture.listing_id == listing.id:
            picture.delete()
            messages.success(request, 'Picture deleted successfully!')
        else:
            messages.error(request, 'Invalid picture.')
        return redirect('edit-listing', listing_id=listing_id)


class UpdateListingStatusView(LoginRequiredMixin, View):
    def post(self, request, listing_id):
        listing = get_object_or_404(Listings, pk=listing_id)

        if listing.status == 'Active':
            listing.status = 'Inactive'
            listing.save()
            return redirect('listings')

        elif listing.status == 'Inactive':
            listing.status = 'Active'
            listing.save()
            return redirect('listings')


class DeleteListingView(LoginRequiredMixin, View):
    def post(self, request, listing_id):
        listing = get_object_or_404(Listings, id=listing_id)

        if listing:
            listing.delete()

            return redirect('listings')


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

            message_type = request.GET.get('message_type', 'All')
            if message_type == 'All':
                messages = Messages.objects.filter(to_user=id).order_by('-id')
            elif message_type == 'Unread':
                messages = Messages.objects.filter(to_user_id=id).filter(status='Unread').order_by('-date_sent')
            elif message_type == 'Read':
                messages = Messages.objects.filter(to_user_id=id).filter(status='Read').order_by('-date_sent')
            elif message_type == 'Sent':
                messages = Messages.objects.filter(from_user_id=id).order_by('-date_sent')

            paginator = Paginator(messages, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            ctx = {
                'user_messages': user_messages,
                'user_unread_messages': user_unread_messages,
                'user_read_messages': user_read_messages,
                'user_sent_messages': user_sent_messages,
                'messages': page_obj,
                # 'page_obj': page_obj,
                'message_type': message_type,
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


class SendNewMessage(LoginRequiredMixin, View):
    def get(self, request, listing_id):
        listing = get_object_or_404(Listings, id=listing_id)
        return render(request, 'sell_it_app/send_new_message.html', {'listing': listing})

    def post(self, request, listing_id):
        listing = get_object_or_404(Listings, id=listing_id)
        sender = request.user.id
        recipient = listing.user_id.id
        message = request.POST.get('message')

        if sender != recipient:
            send_message = Messages.objects.create(
                title=listing.title,
                message=message,
                from_user_id=sender,
                to_user_id=recipient,
                status='Unread',
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('listing-details', listing_id=listing_id)
        else:
            messages.error(request, "You cannot send a message to yourself!")
            return redirect('send-new-message', listing_id=listing_id)


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


class FaqView(View):
    def get(self, request):
        return render(request, 'sell_it_app/faq.html')


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

