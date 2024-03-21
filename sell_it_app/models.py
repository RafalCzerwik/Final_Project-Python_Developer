from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models

# Create your models here.


class User(AbstractUser):
    """
    Custom user model representing users in the system.

    This model extends Django's built-in AbstractUser model to include additional fields.

    Attributes:
        GENDER_CHOICES (tuple): Choices for user gender selection.
        gender (str): Field representing the gender of the user. Defaults to 'F' for Female.
        phone_number (str): Field representing the phone number of the user. Must be 9 digits.
        date_of_birth (datetime.date): Field representing the date of birth of the user.
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


class Category(models.Model):
    """
    Model representing categories of items.

    Attributes:
        CATEGORY_CHOICES (tuple): Choices for category selection.
        name (str): Field representing the name of the category.
        description (str): Field representing the description of the category.
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


class Address(models.Model):
    """
    Model representing user addresses.

    Attributes:
        user_id (int): Field representing the ID of the associated user.
        street_name (str): Field representing the primary street name of the address.
        street_name_secondary (str): Field representing the secondary street name of the address.
        city (str): Field representing the city of the address.
        postal_code (str): Field representing the postal code of the address.
        country (str): Field representing the country of the address.
    """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=255)
    street_name_secondary = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6)
    country = models.CharField(max_length=50)


class Messages(models.Model):
    """
    Model representing messages between users.

    Attributes:
        STATUS_CHOICES (tuple): Choices for message status selection.
        from_user (int): Field representing the sender of the message.
        from_unregistered_user (str): Field representing the email of an unregistered user sender.
        to_user (int): Field representing the recipient of the message.
        title (str): Field representing the title of the message.
        message (str): Field representing the content of the message.
        date_sent (datetime.datetime): Field representing the date the message was sent.
        status (str): Field representing the status of the message.
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


class Listings(models.Model):
    """
    Model representing listings of items for sale or exchange.

    Attributes:
        CONDITION_CHOICES (tuple): Choices for item condition selection.
        OFFER_CHOICES (tuple): Choices for offer type selection.
        PROMOTION_CHOICES (tuple): Choices for promotion status selection.
        STATUS_CHOICES (tuple): Choices for listing status selection.
        user_id (int): Field representing the ID of the associated user.
        category_id (int): Field representing the ID of the associated category.
        address_id (int): Field representing the ID of the associated address.
        condition (str): Field representing the condition of the listed item.
        offer_type (str): Field representing the type of offer for the listing.
        promotion (str): Field representing the promotion status of the listing.
        status (str): Field representing the status of the listing.
        title (str): Field representing the title of the listing.
        description (str): Field representing the description of the listing.
        price (decimal.Decimal): Field representing the price of the listing.
        add_date (datetime.datetime): Field representing the date the listing was added.
    """

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
    """
    Model representing pictures associated with listings.

    Attributes:
        user_id (int): Field representing the ID of the associated user.
        listing (int): Field representing the ID of the associated listing.
        name (str): Field representing the name of the picture.
        image (str): Field representing the image file.
    """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name='pictures')
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='uploads/listing_pictures/',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Avatars(models.Model):
    """
    Model representing user avatars.

    Attributes:
        user_id (int): Field representing the ID of the associated user.
        avatar (str): Field representing the avatar image file.
    """

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='uploads/avatars/',
                               validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])


class Newsletter(models.Model):
    """
    Model representing a newsletter subscription.

    Attributes:
        email (str): Field representing the email address of the subscriber.
    """

    email = models.EmailField(blank=False, null=False)
