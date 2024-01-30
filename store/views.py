from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from urllib3.util import url
from orders.models import OrderProduct

from store.forms import ReviewRatingForm
from .models import Product, ReviewRating, Variation
from category.models import Category
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    keyword = ''

    if 'keyword' in request.GET and request.GET['keyword'] != '':
        keyword = request.GET['keyword']
        products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    elif category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-modified_date')
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-modified_date')
    product_count = products.count()
    
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page", 1)
    try:
        paged_products = paginator.page(page_number)
    except PageNotAnInteger:
        paged_products = paginator.page(1)
    except EmptyPage:
        paged_products = paginator.page(paginator.num_pages)

    context = {
        'products': paged_products,
        'product_count': product_count,
        'keyword': keyword,
        'category_slug': category_slug,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    variations = product.variation_set.all()
    variation_categories = variations.values_list('variation_category', flat=True).distinct()

    try:
        order_product = OrderProduct.objects.filter(user_id=request.user.id, product_id=product.id).exists()
    except OrderProduct.DoesNotExist:
        order_product = None

    reviews = ReviewRating.objects.filter(product=product, status=True)

    context = {
        'product': product,
        'in_cart': in_cart,
        'variation_categories': variation_categories,
        'order_product': order_product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)

@login_required(login_url="login")
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewRatingForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Thank you! Your review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.product_id = product_id
                data.ip = request.META.get('REMOTE_ADDR')
                data.user_id = request.user.id
                data.save()

                messages.success(request, "Thank you! Your review has been submitted.")
                return redirect(url)