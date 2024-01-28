import datetime
import json
import uuid
from django.contrib import messages
from django.db.models import Sum
from django.db.transaction import commit
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.urls import reverse

from carts.models import CartItem
from greatkart import settings
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from django.views.decorators.csrf import csrf_exempt
from accounts.utils import send_order_received_email
from store.models import Product

# Create your views here.

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = total * 0.02
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'tax': tax,
                'total': total,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')
    

@csrf_exempt 
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment( 
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price * item.quantity
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    mail_subject = 'Thank you for your order!'
    email_template = 'orders/order_received_email.html'
    send_order_received_email(request, request.user, order, mail_subject, email_template)

    data = {
        'order_number': order.order_number,
        'payment_id': payment.id,   
    }

    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(id=transID)
        subtotal = order_products.aggregate(total=Sum('product_price')).get('total')
        context = {
            'order': order,
            'order_products': order_products,
            'order_number': order_number,
            'transID': payment.payment_id,
            'payment': payment.status,
            'subtotal': subtotal,
        }
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    return render(request, 'orders/order_complete.html', context)
