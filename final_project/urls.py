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
from django.contrib import admin
from django.urls import path

from sell_it_app.views import (IndexView,
                               LoginView,
                               RegisterView,
                               DashboardView,
                               TestView,
                               SearchView,
                               MyListingsView,
                               MessagesView,
                               AddListingView,
                               SendMessageView,
                               ProfileView,
                               ContactUsView,
                               ListingView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('test/', TestView.as_view(), name='test'),
    path('search/', SearchView.as_view(), name='search'),
    path('listings/', MyListingsView.as_view(), name='listings'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('add-listing/', AddListingView.as_view(), name='add-listing'),
    path('send-message/', SendMessageView.as_view(), name='send-message'),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('listing-details/', ListingView.as_view(), name='listing-details'), #  <int:id>/
]
