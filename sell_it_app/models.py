from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models

# Create your models here.


class User(AbstractUser):
    """
    This User model inherits from Django's AbstractUser.
    The custom fields added include:
    gender: Can be Male (M), Female (F), or Other (O).
    phone_number: Stores the phone number of the user. Phone number must have 9 digits.
    date_of_birth: Stores the user's date of birth.
    """

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


class Address(models.Model):
    """
    The Address model stores the addresses of Users.
    The fields include:
    user_id: Foreign key relationship to a User. This field identifies the User who is associated with the address.
    street_name: This is the primary street name of the address.
    street_name_secondary: This is the secondary street name of the address, if any.
    city: This is the city of the address.
    postal_code: Postal code corresponding to the address.
    country: The country where the address is located.
    """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=255)
    street_name_secondary = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6)
    country = models.CharField(max_length=50)


class Category(models.Model):
    """
    The Category model is used to categorize listings into various categories.
    name: The name of the category. Can be Market, Real estate, Boat, Motorcycle, Car, Work.
    description: A brief description about the category.
    """

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
    """
    The Listings model holds information about a certain listing.
    user_id: A foreign key relation to the User model. Identifies the user who listed the item.
    category_id: Foreign key relation to the Category model. Identifies the category of the listing.
    condition: Can be 'New' or 'Used'.
    offer_type: The type of the listing, can be 'Sell', 'Buy' or 'Free'.
    status: The status of the listing, can be 'ACTIVE' or 'INACTIVE'.
    promotion: State of the listing, can be 'Promoted' or 'Not Promoted'.
    All other fields hold information about the particular listing.
    """

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

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Used')
    offer_type = models.CharField(max_length=20, choices=OFFER_CHOICES, default='Sell')
    promotion = models.CharField(max_length=20, choices=PROMOTION_CHOICES, default='Not Promoted')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    add_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Messages(models.Model):
    """
    The Messages model contains messages between users.
    from_user: A foreign key relation to the User model. Identifies the sender of the message.
    to_user: A foreign key relation to the User model. Identifies the receiver of the message.
    title: The title of the message.
    message: The content of the message.
    date_sent: The date when the message was sent.
    """

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


class Picture(models.Model):
    """
        The Picture model is used to store images of each listing.
        user_id: A foreign key relation to the User model. Identifies the user who uploaded the image.
        listing_id: A foreign key relation to the Listings model. Identifies the listing the picture is attached to.
        name: The name of the image.
        image: The actual image file.
        """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Listings, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='static/images/user-images/',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Avatars(models.Model):
    """
        The Avatars model stores the avatar pictures for each user.
        user_id: A foreign key relation to the User model. Identifies the user to whom the avatar belongs.
        avatar: The actual avatar image file.
        """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='uploads/avatars/',
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Newsletter(models.Model):
    email = models.EmailField(blank=False, null=False)
