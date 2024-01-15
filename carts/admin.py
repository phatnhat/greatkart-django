from django.contrib import admin
from .models import Cart, CartItem
from django.db import models
from django.forms import CheckboxSelectMultiple
from django_dynamic_admin_forms.admin import DynamicModelAdminMixin
from store.models import Product, Variation
from django.forms import ModelForm

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')


class CartItemAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin/cart_item_admin.js',)

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "variations":
    #         try:
    #             object_id = request.resolver_match.kwargs['object_id']
    #             cart_item = CartItem.objects.get(pk=object_id)
    #             product = cart_item.product
    #             kwargs["queryset"] = Variation.objects.filter(product=product)
    #         except CartItem.DoesNotExist:
    #             kwargs["queryset"] = Variation.objects.none()
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    
    list_display = ('id', 'product', 'cart', 'quantity')

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)