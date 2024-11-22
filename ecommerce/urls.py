"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from shop import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.base_view),
    path('home/', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_product/<int:product_id>/', views.order_product, name='order_product'),
    path('success/',views.success_view,name='success'),
    path('accounts/',include('django.contrib.auth.urls')),
    path('logout/', views.logout_view),
    path('signup/', views.signup_view),
    path('api/',include('shop.api.urls'))
]
