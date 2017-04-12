from django.contrib import admin

from .models import *
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=('address','pub_key')

class TokenAdmin(admin.ModelAdmin):
    list_display=('token','chain','read','write')
admin.site.register(User,UserAdmin)
admin.site.register(Tokens,TokenAdmin)
