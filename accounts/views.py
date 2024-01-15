from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from .utils import send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Create your views here.

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect("login")
    return render(request, 'accounts/login.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name, last_name, username, email, password)
            user.phone_number = phone_number
            user.save()

            mail_subject = 'Please activate your account'
            email_template = 'accounts/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            return redirect(f'/accounts/login/?command=verification&email={email}')
        else:
            error = ''.join(list(form.errors.as_data().values())[0][0])
            messages.error(request, error)
            return redirect('register')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is actived.")
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgot(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            mail_subject = 'Reset your password'
            email_template = 'accounts/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Password reset email has been sent to your email address.")
            return redirect('login')
        else:
            messages.error(request, "Account does not exists!")
            return redirect('forgot')
    return render(request, "accounts/forgot.html")


def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, "This link has been expired!")
        return redirect('login')
    
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")
    return render(request, "accounts/reset_password.html")