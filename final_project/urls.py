"""
URL configuration for final_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from sell_it_app.views import (IndexView,
                               LoginView,
                               RegisterView,
                               DashboardView,
                               SearchView,
                               MyListingsView,
                               MessagesView,
                               AddListingView,
                               SendMessageView,
                               ProfileView,
                               ContactUsView,
                               ListingView,
                               LogOutView,
                               MyAddressView,
                               PaymentsView,
                               FavouritesView,
                               SavedSearchesView,
                               AboutUsView,
                               PublicProfileView,
                               MessageStatusUpdateView,
                               MessageDeleteView,
                               ShowMessageView,
                               NewsletterView,
                               EditListingView,
                               EditListingPictureView,
                               DeleteListingView,
                               UpdateListingStatusView,
                               UpdateProfileAvatarView,
                               UpdateProfileView,
                               UpdatePassword,
                               SendNewMessage,
                               CategoryView,
                               FaqView,
                               DeleteListingPicture,
                               ListingGoogleMapsView)


urlpatterns = [
    path('admin/', admin.site.urls),  # OK
    path('', IndexView.as_view(), name='index'),  # OK
    path('login/', LoginView.as_view(), name='login'),  # OK
    path('logout/', LogOutView.as_view(), name='logout'),  # OK
    path('register/', RegisterView.as_view(), name='register'),  # OK
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  # OK
    path('category/<int:category_id>/', CategoryView.as_view(), name='category'),  # OK
    path('profile/', ProfileView.as_view(), name='profile'),  # OK
    path('profile/update-password/', UpdatePassword.as_view(), name='update-password'),  # OK
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),  # OK
    path('update-profile/avatar/', UpdateProfileAvatarView.as_view(), name='update-profile-avatar'),  # OK
    path('public-profile/', PublicProfileView.as_view(), name='public-profile'),  # OK
    path('search/', SearchView.as_view(), name='search'),  # OK
    path('listings/', MyListingsView.as_view(), name='listings'),  # OK
    path('listing/map/<int:listing_id>/', ListingGoogleMapsView.as_view(), name='google-maps'),  # OK
    path('listing-details/<int:listing_id>/', ListingView.as_view(), name='listing-details'),  # OK
    path('add-listing/', AddListingView.as_view(), name='add-listing'),
    path('edit-listing/<int:listing_id>/', EditListingView.as_view(), name='edit-listing'),
    path('edit-listing/<int:listing_id>/picture/', EditListingPictureView.as_view(), name='edit-listing-picture'),
    path('delete-listing-picture/<int:listing_id>/<int:picture_id>/', DeleteListingPicture.as_view(), name='delete-listing-picture'),
    path('listing/update-status/<int:listing_id>/', UpdateListingStatusView.as_view(), name='update-listing-status'),
    path('delete-listing/<int:listing_id>/', DeleteListingView.as_view(), name='delete-listing'),
    path('messages/', MessagesView.as_view(), name='messages'),  # OK
    path('message/update-status/<int:message_id>', MessageStatusUpdateView.as_view(), name='message-update-status'),
    path('message/delete/<int:message_id>', MessageDeleteView.as_view(), name='message-delete'),
    path('send-message/<int:message_id>/', SendMessageView.as_view(), name='send-message'),
    path('send-new-message/<int:listing_id>/', SendNewMessage.as_view(), name='send-new-message'),
    path('show-message/<int:message_id>/', ShowMessageView.as_view(), name='show-message'),
    path('contact/', ContactUsView.as_view(), name='contact'),  # OK
    path('about-us/', AboutUsView.as_view(), name='about-us'),  # OK
    path('faq/', FaqView.as_view(), name='faq'),  # NOT NOW
    path('address/', MyAddressView.as_view(), name='address'),  # NOT NOW
    path('payments/', PaymentsView.as_view(), name='payments'),  # NOT NOW
    path('favourites/', FavouritesView.as_view(), name='favourites'),  # NOT NOW
    path('saved-searches/', SavedSearchesView.as_view(), name='saved-searches'),  # NOT NOW
    path('newsletter/', NewsletterView.as_view(), name='newsletter'),  # OK
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
