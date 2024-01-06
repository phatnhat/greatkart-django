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

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    
    list_display = ('id', 'product', 'cart', 'quantity')

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)