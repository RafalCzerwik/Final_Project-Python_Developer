from django import forms

from sell_it_app.models import Avatars, Listings, Picture, Address, User


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatars
        fields = ['avatar']


class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['image']

        widgets = {'image': forms.ClearableFileInput(attrs={'allow_multiple_selected': True})}


class AddressesForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_name', 'street_name_secondary', 'city', 'postal_code', 'country']


class ListingsForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['category_id', 'title', 'description', 'price', 'condition', 'offer_type']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'phone_number', 'date_of_birth']


class PasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise forms.ValidationError("Passwords don't match!")
        return cleaned_data
