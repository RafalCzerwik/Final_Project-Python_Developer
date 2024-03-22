import random
import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from sell_it_app.forms import AvatarForm, ListingsForm, AddressesForm, PictureForm, ProfileForm, PasswordForm
from sell_it_app.models import Messages, Newsletter, Avatars, Listings, Category, Picture, Address

User = get_user_model()


class IndexView(View):
    """
    View for rendering the index page.

    Methods:
        get(self, request): Handles GET requests to the index page.
    """

    def get(self, request):
        """
        Handles GET requests to the index page.

        Retrieves promoted and recently added listings, shuffles promoted listings,
        selects a subset for the carousel, and renders the index page with the context.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered index page with the context.
        """

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
    View for handling user login.

    Methods:
        get(self, request): Handles GET requests to the login page.
        post(self, request, *args, **kwargs): Handles POST requests to authenticate users.
    """

    def get(self, request):
        """
        Handles GET requests to the login page.

        Renders the login page.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered login page.
        """

        return render(request, 'sell_it_app/login.html')

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to authenticate users.

        Authenticates user credentials and redirects to the dashboard upon successful login.
        Sets a cookie to indicate user authentication status.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to the dashboard upon successful login.
            HttpResponse: The rendered login page with an error message if login fails.
        """

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            expiration_time = datetime.datetime.now() + datetime.timedelta(hours=2)
            response = redirect('dashboard')
            response.set_cookie('user_authenticated', 'true', expires=expiration_time)

            return response
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'sell_it_app/login.html', {'error_message': error_message})


class LogOutView(LoginRequiredMixin, View):
    """
    View for logging out the user.

    Redirects to the index page after successful logout.

    Requires the user to be logged in.
    """

    def get(self, request):
        """
        Logs out the user and redirects to the index page.

        Returns:
            HttpResponseRedirect: Redirects to the index page.
        """

        logout(request)
        return redirect('index')


class RegisterView(View):
    """
    View for user registration.

    GET request renders the registration form.
    POST request processes the form data for user registration.
    """

    def get(self, request):
        """
        Renders the registration form.

        Returns:
            HttpResponse: Rendered registration form.
        """

        return render(request, 'sell_it_app/register.html')

    def post(self, request, *args, **kwargs):
        """
        Processes the form data for user registration.

        Checks for username availability and form validity before creating a new user.

        Returns:
            HttpResponseRedirect: Redirects to the login page after successful registration.
            HttpResponse: Rendered registration form with error messages if registration fails.
        """

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
    """
    View for displaying listings within a specific category.

    GET request renders the category page with listings filtered by category.
    """

    def get(self, request, category_id):
        """
        Renders the category page with listings filtered by category.

        Args:
            request (HttpRequest): HTTP request object.
            category_id (int): ID of the category.

        Returns:
            HttpResponse: Rendered category page.
        """

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
    """
    View for rendering the user dashboard.

    Requires the user to be logged in.
    """

    def get(self, request):
        """
        Renders the user dashboard.

        Returns:
            HttpResponse: Rendered dashboard page with user avatar.
        """

        avatar = Avatars.objects.filter(user_id=request.user).last()
        return render(request, 'sell_it_app/dashboard.html', {'avatar': avatar})


class ProfileView(LoginRequiredMixin, View):
    """
    View for rendering the user profile page.

    GET request renders the user profile page with the avatar form.

    Requires the user to be logged in.
    """

    def get(self, request):
        """
        Renders the user profile page with the avatar form.

        Returns:
            HttpResponse: Rendered profile page with user avatar and avatar form.
        """

        avatar = Avatars.objects.filter(user_id=request.user).last()
        form = AvatarForm()
        return render(request, 'sell_it_app/profile.html', {'avatar': avatar, 'form': form})


class UpdateProfileView(LoginRequiredMixin, View):
    """
    View for updating user profile information.

    GET request renders the profile page with the profile update form.
    POST request processes the form data for updating user profile information.

    Requires the user to be logged in.
    """

    def get(self, request):
        """
        Renders the profile page with the profile update form.

        Returns:
            HttpResponse: Rendered profile page with user profile and profile update form.
        """

        user = User.objects.get(id=request.user.id)
        form = ProfileForm(instance=user)
        return render(request, 'sell_it_app/profile.html', {'user': user, 'form': form})

    def post(self, request):
        """
        Processes the form data for updating user profile information.

        Returns:
            HttpResponseRedirect: Redirects to the profile page after successful profile update.
            HttpResponse: Rendered profile page with error messages if profile update fails.
        """

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
    """
    View for updating user password.

    POST request processes the form data for updating user password.

    Requires the user to be logged in.
    """

    def post(self, request):
        """
        Processes the form data for updating user password.

        Returns:
            HttpResponseRedirect: Redirects to the profile page after successful password update.
            HttpResponse: Rendered profile page with error messages if password update fails.
        """

        form = PasswordForm(request.POST)
        avatar = Avatars.objects.filter(user_id=request.user).first()
        user = request.user
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data.get('new_password')
            if len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters long!')
                return render(request, 'sell_it_app/profile.html', {'form': form, 'user': user, 'avatar': avatar})

            user.set_password(new_password)
            user.save()

            messages.success(request, 'Password updated successfully!')
            update_session_auth_hash(request, user)
            return redirect('profile')

        return render(request, 'sell_it_app/profile.html', {'form': form, 'user': user, 'avatar': avatar})


class UpdateProfileAvatarView(LoginRequiredMixin, View):
    """
    View for updating user profile avatar.

    POST request processes the form data for updating user profile avatar.

    Requires the user to be logged in.
    """

    def post(self, request):
        """
        Processes the form data for updating user profile avatar.

        Returns:
            HttpResponseRedirect: Redirects to the profile page after successful avatar update.
            HttpResponse: Rendered profile page with error messages if avatar update fails.
        """

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
    """
    View for rendering public user profile page.

    GET request renders the public user profile page.
    """

    def get(self, request):
        """
        Renders the public user profile page.

        Returns:
            HttpResponse: Rendered public user profile page.
        """

        return render(request, 'sell_it_app/public_profile.html')


class SearchView(View):
    """
    View for searching listings.

    GET request processes the search query and renders the search results page.

    Attributes:
        query (str): The search query entered by the user.
        searching (QuerySet): Queryset of listings filtered by the search query.
    """

    def get(self, request):
        """
        Processes the search query and renders the search results page.

        Returns:
            HttpResponse: Rendered search results page.
        """

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
    """
    View for displaying user's listings.

    GET request renders the user's listings page.

    Attributes:
        all_listings (int): Total count of user's listings.
        active_listings (int): Count of active listings belonging to the user.
        inactive_listings (int): Count of inactive listings belonging to the user.
        listings_type (str): Type of listings to display ('All', 'Active', 'Inactive').
    """

    def get(self, request):
        """
        Renders the user's listings page.

        Returns:
            HttpResponse: Rendered user's listings page.
        """

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
    """
    View for displaying individual listing details.

    GET request renders the listing page with details and pictures.

    Attributes:
        user (User): The current user accessing the page.
        listing (Listing): The listing object being viewed.
        avatar (Avatar): The avatar of the user who created the listing.
        pictures (QuerySet): Queryset of pictures related to the listing.
    """

    def get(self, request, listing_id):
        """
        Renders the listing page with details and pictures.

        Returns:
            HttpResponse: Rendered listing page.
        """

        user = request.user
        if user.is_authenticated:
            listing = get_object_or_404(Listings, pk=listing_id)
            avatar = Avatars.objects.filter(user_id=request.user).last()
            pictures = Picture.objects.filter(listing=listing_id)
            return render(request, 'sell_it_app/listing.html', {
                'listing': listing,
                'avatar': avatar,
                'pictures': pictures,
            })
        else:
            listing = get_object_or_404(Listings, pk=listing_id)
            pictures = Picture.objects.filter(listing=listing_id)
            return render(request, 'sell_it_app/listing.html', {'listing': listing, 'pictures': pictures})


class ListingGoogleMapsView(View):
    """
    View for displaying Google Maps for a specific listing.

    GET request renders the Google Maps page for the specified listing.

    Attributes:
        listing_id (int): ID of the listing.
    """

    def get(self, request, listing_id):
        """
        Renders the Google Maps page for the specified listing.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponse: Rendered Google Maps page.
        """

        listing = get_object_or_404(Listings, pk=listing_id)
        return render(request, 'sell_it_app/google_maps.html', {'listing': listing})


class AddListingView(LoginRequiredMixin, View):
    """
    View for adding a new listing.

    GET request renders the add listing form.
    POST request processes the form data for adding a new listing.

    Requires the user to be logged in.
    """

    def get(self, request):
        """
        Renders the add listing form.

        Returns:
            HttpResponse: Rendered add listing form.
        """

        categories = Category.objects.all()

        ctx = {
            'categories': categories,
        }
        return render(request, 'sell_it_app/add_listing.html', ctx)

    def post(self, request):
        """
        Processes the form data for adding a new listing.

        Returns:
            HttpResponseRedirect: Redirects to the newly added listing details page.
            HttpResponse: Rendered add listing form with error messages if form submission fails.
        """

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
            if len(request.FILES.getlist('image')) > 8:
                messages.error(request, 'You have exceeded a maximum of 8 pictures!')
                return render(request, 'sell_it_app/add_listing.html', ctx)
            else:
                for file in request.FILES.getlist('image'):
                    picture = Picture(user_id=request.user, image=file, listing=listing)
                    picture.save()
                    pictures.append(picture)
                ctx['pictures'] = pictures

        if listing_form.is_valid() and picture_form.is_valid() and address_form.is_valid():
            # return render(request, 'sell_it_app/listing.html', ctx)
            return redirect('listing-details', listing_id=listing.id)
        else:
            error_message = 'Error! Please check and try again!'
            return render(request, 'sell_it_app/add_listing.html', {'error_message': error_message})


class EditListingView(LoginRequiredMixin, View):
    """
    View for editing a listing.

    GET request renders the edit listing form.
    POST request processes the form data for updating the listing details.

    Requires the user to be logged in.
    """

    def get(self, request, listing_id):
        """
        Renders the edit listing form.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponse: Rendered edit listing form.
        """

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
        """
        Processes the form data for updating the listing details.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponseRedirect: Redirects to the updated listing details page.
            HttpResponse: Rendered edit listing form with error messages if form submission fails.
        """

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
    """
    View for editing a listing's pictures.

    GET request renders the edit listing form with picture uploads.
    POST request processes the form data for uploading new pictures to the listing.

    Requires the user to be logged in.
    """

    def get(self, request, listing_id):
        """
        Renders the edit listing form with picture uploads.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponse: Rendered edit listing form with picture uploads.
        """

        listing = get_object_or_404(Listings, pk=listing_id)
        return render(request, 'sell_it_app/edit_listing.html', {'listing': listing})

    def post(self, request, listing_id):
        """
        Processes the form data for uploading new pictures to the listing.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponseRedirect: Redirects to the updated listing details page.
            HttpResponse: Rendered edit listing form with error messages if form submission fails.
        """

        listing = get_object_or_404(Listings, pk=listing_id)
        user = request.user
        if listing.user_id != user:
            return HttpResponseForbidden("You do not have permission to edit this listing's picture.")

        picture_form = PictureForm(request.POST, request.FILES)

        if picture_form.is_valid():
            existing_pictures = Picture.objects.filter(listing_id=listing.id, user_id=request.user).count()
            new_picture_count = len(request.FILES.getlist('image'))
            total_pictures = existing_pictures + new_picture_count
            if total_pictures > 8:
                messages.error(request, 'You can upload a maximum 8 pictures!')
            else:
                for file in request.FILES.getlist('image'):
                    picture = Picture(user_id=request.user, image=file, listing=listing)
                    picture.save()
                messages.success(request, 'Picture uploaded successfully!')
            return redirect('edit-listing', listing.id)

        return render(request, 'sell_it_app/edit_listing.html', {'listing': listing})


class DeleteListingPicture(LoginRequiredMixin, View):
    """
    View for deleting a listing's picture.

    POST request processes the form data for deleting a picture associated with a listing.

    Requires the user to be logged in.
    """

    def post(self, request, listing_id, picture_id):
        """
        Processes the form data for deleting a picture associated with a listing.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.
            picture_id (int): ID of the picture.

        Returns:
            HttpResponseRedirect: Redirects to the updated listing details page.
        """

        listing = get_object_or_404(Listings, pk=listing_id)
        picture = Picture.objects.get(pk=picture_id)

        if listing.user_id != request.user:
            return HttpResponseForbidden("You do not have permission to edit this listing's picture.")

        if picture.listing_id == listing.id:
            picture.delete()
            messages.success(request, 'Picture deleted successfully!')
        else:
            messages.error(request, 'Invalid picture.')
        return redirect('edit-listing', listing_id=listing_id)


class UpdateListingStatusView(LoginRequiredMixin, View):
    """
    View for updating the status of a listing.

    POST request processes the form data for updating the status of a listing.

    Requires the user to be logged in.
    """

    def post(self, request, listing_id):
        """
        Processes the form data for updating the status of a listing.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponseRedirect: Redirects to the listings page after updating the status.
        """

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
    """
    View for deleting a listing.

    POST request processes the form data for deleting a listing.

    Requires the user to be logged in.
    """

    def post(self, request, listing_id):
        """
        Processes the form data for deleting a listing.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing.

        Returns:
            HttpResponseRedirect: Redirects to the listings page after deleting the listing.
        """

        listing = get_object_or_404(Listings, id=listing_id)

        if listing:
            listing.delete()

            return redirect('listings')


class MessagesView(LoginRequiredMixin, View):
    """
    View for displaying messages.

    Attributes:
        user (User): The current authenticated user.
        id (int): The ID of the current authenticated user.
        messages (QuerySet): The messages related to the current user.
        user_messages (int): The total number of messages received by the user.
        user_unread_messages (int): The number of unread messages received by the user.
        user_read_messages (int): The number of read messages received by the user.
        user_sent_messages (int): The number of messages sent by the user.
        message_type (str): The type of messages to display (All, Unread, Read, Sent).
        paginator (Paginator): Paginator object for paginating messages.
        page_number (str): The current page number of the paginated messages.
        page_obj (Page): Page object containing the messages for the current page.
        ctx (dict): Context dictionary containing data to be rendered in the template.
    """

    def get(self, request):
        """
        Handles GET requests to display messages.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            render: Renders the 'messages.html' template with context data.
        """
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
    """
    View for updating the status of a message.

    POST request updates the status of the message to either 'Read' or 'Unread'.

    Attributes:
        message (Messages): The message to update the status.
    """

    def post(self, request, message_id):
        """
        Updates the status of the message to either 'Read' or 'Unread'.

        Args:
            request (HttpRequest): HTTP request object.
            message_id (int): ID of the message to update.

        Returns:
            HttpResponseRedirect: Redirects to the 'messages' page.
        """

        message = get_object_or_404(Messages, id=message_id)
        if request.user.id != message.from_user_id and request.user.id != message.to_user_id:
            return HttpResponseForbidden("You do not have permission to change this message's status.")

        if message.status == 'Unread':
            message.status = 'Read'
            message.save()
            return redirect('messages')
        if message.status == 'Read':
            message.status = 'Unread'
            message.save()
            return redirect('messages')


class MessageDeleteView(LoginRequiredMixin, View):
    """
    View for deleting a message.

    POST request deletes the specified message.

    Attributes:
        message (Messages): The message to delete.
    """

    def post(self, request, message_id):
        """
        Deletes the specified message.

        Args:
            request (HttpRequest): HTTP request object.
            message_id (int): ID of the message to delete.

        Returns:
            HttpResponseRedirect: Redirects to the 'messages' page.
        """

        message = get_object_or_404(Messages, id=message_id)

        if message:
            message.delete()
            return redirect('messages')


class ShowMessageView(LoginRequiredMixin, View):
    """
    View for displaying a single message.

    GET request renders the 'message.html' template with message details.

    Attributes:
        message (Messages): The message to display.
    """

    def get(self, request, message_id):
        """
        Renders the 'message.html' template with message details.

        Args:
            request (HttpRequest): HTTP request object.
            message_id (int): ID of the message to display.

        Returns:
            HttpResponse: Renders the 'message.html' template.
        """

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
    """
    View for sending a message as a response to an existing message.

    GET request renders the 'message.html' template with the current message.
    POST request sends the new message and renders the 'message.html' template
    with appropriate success or error messages.

    Attributes:
        current_message (Messages): The current message being responded to.
    """

    def get(self, request, message_id):
        """
        Renders the 'message.html' template with the current message.

        Args:
            request (HttpRequest): HTTP request object.
            message_id (int): ID of the message to respond to.

        Returns:
            HttpResponse: Renders the 'message.html' template.
        """

        current_message = get_object_or_404(Messages, pk=message_id)
        return render(request, 'sell_it_app/message.html', {'current_message': current_message})

    def post(self, request, message_id):
        """
        Sends a new message as a response to the current message and renders the
        'message.html' template with appropriate success or error messages.

        Args:
            request (HttpRequest): HTTP request object.
            message_id (int): ID of the message to respond to.

        Returns:
            HttpResponse: Renders the 'message.html' template.
        """

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
    """
    View for sending a new message to a listing owner.

    GET request renders the 'send_new_message.html' template.
    POST request sends the message and redirects to the listing details page
    with appropriate success or error messages.

    Attributes:
        listing (Listings): The listing to which the message is being sent.
    """

    def get(self, request, listing_id):
        """
        Renders the 'send_new_message.html' template with the listing details.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing to which the message is sent.

        Returns:
            HttpResponse: Renders the 'send_new_message.html' template.
        """

        listing = get_object_or_404(Listings, id=listing_id)
        return render(request, 'sell_it_app/send_new_message.html', {'listing': listing})

    def post(self, request, listing_id):
        """
        Sends a new message to the owner of the listing and redirects to the listing
        details page with appropriate success or error messages.

        Args:
            request (HttpRequest): HTTP request object.
            listing_id (int): ID of the listing to which the message is sent.

        Returns:
            HttpResponseRedirect: Redirects to the listing details page.
        """

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
    """
    View for displaying user's address information.

    Only accessible for authenticated users.

    GET request renders the 'my_address.html' template.
    """

    def get(self, request):
        """
        Renders the 'my_address.html' template.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the 'my_address.html' template.
        """

        return render(request, 'sell_it_app/my_address.html')


class PaymentsView(LoginRequiredMixin, View):
    """
    View for displaying payment information.

    Only accessible for authenticated users.

    GET request renders the 'payments.html' template.
    """

    def get(self, request):
        """
        Renders the 'payments.html' template.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the 'payments.html' template.
        """

        return render(request, 'sell_it_app/payments.html')


class FavouritesView(LoginRequiredMixin, View):
    """
    View for displaying user's favourite items.

    Only accessible for authenticated users.

    GET request renders the 'favourites.html' template.
    """

    def get(self, request):
        """
        Renders the 'favourites.html' template.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the 'favourites.html' template.
        """

        return render(request, 'sell_it_app/favourites.html')


class SavedSearchesView(LoginRequiredMixin, View):
    """
    View for displaying user's saved searches.

    Only accessible for authenticated users.

    GET request renders the 'saved_searches.html' template.
    """

    def get(self, request):
        """
        Renders the 'saved_searches.html' template.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the 'saved_searches.html' template.
        """

        return render(request, 'sell_it_app/saved_searches.html')


class AboutUsView(View):
    """
    View for displaying information about the website.

    GET request renders the 'about_us.html' template.
    """

    def get(self, request):
        """
        Renders the 'about_us.html' template.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the 'about_us.html' template.
        """

        return render(request, 'sell_it_app/about_us.html')


class FaqView(View):
    """
    View for displaying Frequently Asked Questions (FAQ).

    GET request renders the 'faq.html' template.
    """

    def get(self, request):
        """
        Renders the 'faq.html' template.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the 'faq.html' template.
        """

        return render(request, 'sell_it_app/faq.html')


class ContactUsView(View):
    """
    View for handling contact form submissions.

    GET request renders the contact form.
    POST request processes the form data and sends a message.

    If the user is authenticated, the message is sent from the user to the admin.
    If the user is not authenticated, the message is sent from an unregistered email address to the admin.
    """

    def get(self, request):
        """
        Renders the contact form.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the contact form.
        """

        return render(request, 'sell_it_app/contact_us.html')

    def post(self, request):
        """
        Processes the form data and sends a message.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the contact form with success or error messages.
        """

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
    """
    View for subscribing to the newsletter.

    GET request renders the newsletter subscription form.
    POST request processes the form data for subscribing to the newsletter.
    """

    def get(self, request):
        """
        Renders the newsletter subscription form.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponse: Renders the newsletter subscription form.
        """

        return render(request, 'sell_it_app/newsletter.html')

    def post(self, request):
        """
        Processes the form data for subscribing to the newsletter.

        Args:
            request (HttpRequest): HTTP request object.

        Returns:
            HttpResponseRedirect: Redirects to the newsletter page after subscription.
        """

        email = request.POST.get('email')
        registered_email = Newsletter.objects.filter(email=email).last()

        if registered_email:
            messages.error(request, 'Email already registered!')
            return redirect('newsletter')
        else:
            subscribe = Newsletter.objects.create(email=email)

        return redirect('newsletter')
