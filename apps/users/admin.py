from django.contrib import admin

from users.models import CustomUser, Profile, UserPhoto

admin.site.register([CustomUser, Profile, UserPhoto])
