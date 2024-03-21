from django import forms

from sell_it_app.models import Avatars, Listings, Picture, Address, User


class AvatarForm(forms.ModelForm):
    """
    A form for updating user avatars.

    Attributes:
    - avatar: A field representing the avatar image of the user.
    """
    class Meta:
        model = Avatars
        fields = ['avatar']


class PictureForm(forms.ModelForm):
    """
    A form for uploading pictures.

    Attributes:
    - image: A field representing the image file to be uploaded.
    """
    class Meta:
        model = Picture
        fields = ['image']

        widgets = {'image': forms.ClearableFileInput(attrs={'allow_multiple_selected': True})}


class AddressesForm(forms.ModelForm):
    """
    A form for updating user addresses.

    Attributes:
    - street_name: A field representing the primary street name of the address.
    - street_name_secondary: A field representing the secondary street name of the address.
    - city: A field representing the city of the address.
    - postal_code: A field representing the postal code of the address.
    - country: A field representing the country of the address.
    """
    class Meta:
        model = Address
        fields = ['street_name', 'street_name_secondary', 'city', 'postal_code', 'country']


class ListingsForm(forms.ModelForm):
    """
    A form for creating or updating listings.

    Attributes:
    - category_id: A field representing the category ID of the listing.
    - title: A field representing the title of the listing.
    - description: A field representing the description of the listing.
    - price: A field representing the price of the listing.
    - condition: A field representing the condition of the listed item.
    - offer_type: A field representing the type of offer for the listing.
    """

    class Meta:
        model = Listings
        fields = ['category_id', 'title', 'description', 'price', 'condition', 'offer_type']


class ProfileForm(forms.ModelForm):
    """
    A form for updating user profiles.

    Attributes:
    - first_name: A field representing the first name of the user.
    - last_name: A field representing the last name of the user.
    - gender: A field representing the gender of the user.
    - phone_number: A field representing the phone number of the user.
    - date_of_birth: A field representing the date of birth of the user.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'phone_number', 'date_of_birth']


class PasswordForm(forms.Form):
    """
    A form for changing user passwords.

    Attributes:
    - new_password: A field representing the new password.
    - new_password_confirm: A field representing the confirmation of the new password.
    """
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """
        Clean method to validate password confirmation.

        Raises:
        - ValidationError: If the passwords don't match.
        """
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise forms.ValidationError("Passwords don't match!")
        return cleaned_data
