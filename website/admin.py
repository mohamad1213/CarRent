from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Car)
admin.site.register(Faq)
admin.site.register(Year)
admin.site.register(Order)
# admin.site.register(Customer)
admin.site.register(Location)
admin.site.register(Additions)
admin.site.register(canceledOrders)
# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin):
#     list_display = ('name', 'email', 'phone_number', 'car', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('name', 'email', 'message')