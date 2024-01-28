from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from store.models import Product, Variation
from carts.models import CartItem

def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {'products': products}
    
    return render(request, 'home.html', context)


def get_variations(request):
    product_id = request.GET.get('product_id')
    cart_item_id = int(request.GET.get('cart_item_id')) or None
    if cart_item_id:
        cart_item = CartItem.objects.get(id=cart_item_id)
        variations = Variation.objects.filter(product_id=product_id)
        variations_checked = [f'{variation.variation_category} - {variation.variation_value}' for variation in cart_item.variations.all()]
        variation_choices = [dict(id=v.id, value=str(v), checked=True if str(v) in variations_checked else False) for v in variations]
    else:
        variations = Variation.objects.filter(product_id=product_id)
        variation_choices = [dict(id=v.id, value=str(v), checked=False) for v in variations]
    
    return JsonResponse(variation_choices, safe=False)