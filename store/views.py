from django.shortcuts import render, get_object_or_404
from .models import Product, Variation
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
    
    paginator = Paginator(products, 1)
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
    context = {
        'product': product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)