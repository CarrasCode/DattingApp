# Register your models here.
from django.contrib import admin

from apps.chat.models import Message

admin.site.register([Message])
