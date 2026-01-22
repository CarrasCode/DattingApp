from django.contrib import admin

from apps.users.models import CustomUser, Profile, UserPhoto

admin.site.register([CustomUser, Profile, UserPhoto])
