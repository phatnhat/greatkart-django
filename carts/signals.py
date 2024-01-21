from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from carts.models import Cart, CartItem
from carts.views import _cart_id

@receiver(user_logged_in)
def add_cart_to_user(sender, request, **kwargs):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        is_cart_item_exist = CartItem.objects.filter(cart= cart).exists()
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(cart=cart)
            for item in cart_item:
                item.user = request.user
                item.save()
    except Exception as e:
        pass