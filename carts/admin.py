from django import forms
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


class CartItemAdminForm(forms.ModelForm):
    variations = forms.ModelMultipleChoiceField(
        queryset=Variation.objects.none(),  # Set an initial empty queryset
        widget=admin.widgets.FilteredSelectMultiple('Variations', False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product_id = self.initial.get('product')
        if product_id:
            self.fields['variations'].queryset = Variation.objects.filter(product_id=product_id, is_active=True)

    class Meta:
        model = Cart
        fields = '__all__'


class CartItemAdmin(admin.ModelAdmin):
    form = CartItemAdminForm
    list_display = ('id', 'product', 'cart', 'quantity')
    # readonly_fields = ('get_variations',)
    # fields = ('user', 'product', 'get_variations')

    def get_variations(self, obj):
        return obj.variations.all()

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)