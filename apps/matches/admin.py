# Register your models here.
from django.contrib import admin

from apps.matches.models import Match, Swipe

admin.site.register([Match, Swipe])
