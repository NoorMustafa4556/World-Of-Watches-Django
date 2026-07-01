from django.contrib import admin
from .models import User, Order, Watch, Testimonial, Cart, CartItem, ManualPaymentMethod
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'watch', 'quantity', 'status', 'payment_method', 'online_wallet', 'order_date')
    list_filter = ('status', 'payment_method', 'online_wallet')
    readonly_fields = ('order_date',)

class ManualPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_title', 'account_number', 'is_active')

admin.site.register(User)
admin.site.register(Order, OrderAdmin)
admin.site.register(Watch)
admin.site.register(Testimonial)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ManualPaymentMethod, ManualPaymentMethodAdmin)
