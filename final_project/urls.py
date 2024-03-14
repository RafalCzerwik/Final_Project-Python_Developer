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
                               UpdatePassword)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update-password/', UpdatePassword.as_view(), name='update-password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('update-profile/avatar/', UpdateProfileAvatarView.as_view(), name='update-profile-avatar'),
    path('public-profile/', PublicProfileView.as_view(), name='public-profile'),
    path('search/', SearchView.as_view(), name='search'),
    path('listings/', MyListingsView.as_view(), name='listings'),
    path('listing-details/<int:listing_id>/', ListingView.as_view(), name='listing-details'),
    path('add-listing/', AddListingView.as_view(), name='add-listing'),
    path('edit-listing/<int:listing_id>/', EditListingView.as_view(), name='edit-listing'),
    path('edit-listing/<int:listing_id>/picture/', EditListingPictureView.as_view(), name='edit-listing-picture'),
    path('listing/update-status/<int:listing_id>/', UpdateListingStatusView.as_view(), name='update-listing-status'),
    path('delete-listing/<int:listing_id>/', DeleteListingView.as_view(), name='delete-listing'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('message/update-status/<int:message_id>', MessageStatusUpdateView.as_view(), name='message-update-status'),
    path('message/delete/<int:message_id>', MessageDeleteView.as_view(), name='message-delete'),
    path('send-message/<int:message_id>/', SendMessageView.as_view(), name='send-message'),
    path('show-message/<int:message_id>/', ShowMessageView.as_view(), name='show-message'),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('about-us/', AboutUsView.as_view(), name='about-us'),
    path('address/', MyAddressView.as_view(), name='address'),
    path('payments/', PaymentsView.as_view(), name='payments'),
    path('favourites/', FavouritesView.as_view(), name='favourites'),
    path('saved-searches/', SavedSearchesView.as_view(), name='saved-searches'),
    path('newsletter/', NewsletterView.as_view(), name='newsletter'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
