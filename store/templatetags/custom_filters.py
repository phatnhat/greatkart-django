from django import template

register = template.Library()

@register.filter
def variation_filter(product, category):
    try:
        variations = product.variation_set.filter(variation_category=category)
        return variations   
    except AttributeError as e:
        return None