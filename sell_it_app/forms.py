from django import forms

from sell_it_app.models import Avatars


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatars
        fields = ['avatar']
