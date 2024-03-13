from django import forms

from sell_it_app.models import Avatars, Listings, Picture, Address


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatars
        fields = ['avatar']


class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['image']


class AddressesForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_name', 'street_name_secondary', 'city', 'postal_code', 'country']


class ListingsForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['category_id', 'title', 'description', 'price', 'condition', 'offer_type']
