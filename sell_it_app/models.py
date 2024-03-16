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
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='F')
    phone_number = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        validators=[RegexValidator(regex='^[0-9]{9}$',
                                   message='Phone number must have 9 digits!')])
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


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


class Address(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=255)
    street_name_secondary = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6)
    country = models.CharField(max_length=50)


class Messages(models.Model):

    STATUS_CHOICES = (
        ('Read', 'Read'),
        ('Unread', 'Unread')
    )

    from_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='from_messages')
    from_unregistered_user = models.EmailField(null=True, blank=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_messages')
    title = models.CharField(max_length=60)
    message = models.TextField(max_length=1000)
    date_sent = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default='Unread')

    def __str__(self):
        return self.title, self.from_unregistered_user


class Listings(models.Model):

    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Used', 'Used'),
    )

    OFFER_CHOICES = (
        ('Sell', 'Sell'),
        ('Buy', 'Buy'),
        ('For Free', 'For free'),
    )

    PROMOTION_CHOICES = (
        ('Promoted', 'Promoted'),
        ('Not Promoted', 'Not Promoted'),
    )

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    # picture_id = models.ForeignKey(Picture, on_delete=models.CASCADE)
    address_id = models.ForeignKey(Address, on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Used')
    offer_type = models.CharField(max_length=20, choices=OFFER_CHOICES, default='Sell')
    promotion = models.CharField(max_length=20, choices=PROMOTION_CHOICES, default='Not Promoted')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Picture(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name='pictures')
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='uploads/listing_pictures/',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Avatars(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='uploads/avatars/',
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Newsletter(models.Model):
    email = models.EmailField(blank=False, null=False)
