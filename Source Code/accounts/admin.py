from dataclasses import field
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email','first_name','last_name', 'username', 'last_login', 'is_active', 'date_joined')

    # when clicked on Name,...

    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fileds = ('last_login','date_joined')

    ordering = ('-date_joined',) # comma is used to fix the issue of tuple

    #in case of custom user model

    filter_horizontal = ()
    list_filter = ()
    fieldsets= ()


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width= "30" style="border-radius:50%;">'.format(object.profile_picture.url))

    thumbnail.short_description = ' Profile Picture'

    list_display = ('thumbnail','user','city','prov')


admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)