from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('', views.dashboard, name="dashboard"),
    path('forgot/', views.forgot, name="forgot"),
    path('reset_password_confirm/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('reset_password/', views.reset_password, name="reset_password"),
]
