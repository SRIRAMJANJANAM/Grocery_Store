from django.contrib import admin
from shop.models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]
admin.site.register(Customer,CustomerAdmin)



class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','description','price','image']
admin.site.register(Product,ProductAdmin)


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)