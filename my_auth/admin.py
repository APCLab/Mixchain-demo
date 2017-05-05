from django.contrib import admin

from .models import *
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=('address','pub_key')

class TokenAdmin(admin.ModelAdmin):
    list_display=('token','chain','read','write')

class BidAdmin(admin.ModelAdmin):
    list_display=('number','txid')

admin.site.register(User,UserAdmin)
admin.site.register(Tokens,TokenAdmin)
admin.site.register(Bid,BidAdmin)
