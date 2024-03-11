from django.contrib import admin

from sell_it_app.models import User, Category, Address, Listings, Messages, Picture, Avatars, Newsletter

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Listings)
admin.site.register(Messages)
admin.site.register(Picture)
admin.site.register(Avatars)
admin.site.register(Newsletter)