from django import forms
from django.conf import settings
from django.utils.html import format_html
from paypal.standard.forms import PayPalPaymentsForm

from orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']


class CustomPayPalPaymentsForm(PayPalPaymentsForm):
    def show(self):
        return format_html(f'''<form action="{self.get_login_url()}" method="post">
                                {self.as_p()}
                                <input type="image" src="/static/images/misc/paypal.png" name="submit" alt="Buy it Now" style="width:100%;" />
                            </form>''')
