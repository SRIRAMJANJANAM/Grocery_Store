from django.urls import path,include
from rest_framework import routers
from shop.api.views import ProductCRUDCBV
router=routers.DefaultRouter()
router.register('Product',ProductCRUDCBV)
urlpatterns=[
    path('',include(router.urls))
]