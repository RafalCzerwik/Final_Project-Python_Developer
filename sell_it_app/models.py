from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models

# Create your models here.


class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    phone_number = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        validators=[RegexValidator(regex='^[0-9]{9}$',
                                   message='Phone number must have 9 digits!')])
    date_of_birth = models.DateField(blank=True, null=True)


class Address(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=255)
    street_name_secondary = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6)
    country = models.CharField(max_length=50)


class Category(models.Model):
    CATEGORY_CHOICES = (
        ('Market', 'Market'),
        ('Real estate', 'Real estate'),
        ('Boat', 'Boat'),
        ('Motorcycle', 'Motorcycle'),
        ('Car', 'Car'),
        ('Work', 'Work'),
    )

    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Market')
    description = models.TextField(max_length=255, blank=True)


class Listings(models.Model):
    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Used', 'Used'),
    )

    OFFER_CHOICES = (
        ('Sell', 'Sell'),
        ('Buy', 'But'),
        ('For Free', 'For free'),
    )

    PROMOTION_CHOICES = (
        ('Promoted', 'Promoted'),
        ('Not Promoted', 'Not Promoted'),
    )

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Used')
    offer_type = models.CharField(max_length=20, choices=OFFER_CHOICES, default='Sell')
    promotion = models.CharField(max_length=20, choices=PROMOTION_CHOICES, default='Not Promoted')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pictures = models.ForeignKey(Picture, on_delete=models.CASCADE)
    add_date = models.DateField(auto_now_add=True)


class Messages(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    message = models.TextField(max_length=1000)
    date_sent = models.DateField(auto_now_add=True)


class Picture(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='/static/images/user-images/',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Avatars(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='/static/images/avatars/',
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
