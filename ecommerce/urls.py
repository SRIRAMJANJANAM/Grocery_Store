```python
"""
URL configuration for ecommerce project.
"""

from django.contrib import admin
from django.urls import path, include
from shop import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.base_view, name='base'),
    path('home/', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('order_product/<int:product_id>/', views.order_product, name='order_product'),

    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    path('success/', views.success_view, name='success'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('logs/', views.navi_view, name='logs'),

    path('api/', include('shop.api.urls')),
]

# Serve media files (images)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
