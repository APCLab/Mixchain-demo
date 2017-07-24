from django.contrib import admin

from .models import *
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=('address','pub_key')

class TokenAdmin(admin.ModelAdmin):
    list_display=('token','chain','read','write')

class BidAdmin(admin.ModelAdmin):
    list_display=('number','txid','chain','pub_key1','pri_key1')

class list_BidAdmin(admin.ModelAdmin):
    list_display=('list_id','price','number','bid_txid')

admin.site.register(User,UserAdmin)
admin.site.register(Tokens,TokenAdmin)
admin.site.register(Bid,BidAdmin)
admin.site.register(list_Bid,list_BidAdmin)

