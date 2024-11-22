from rest_framework import viewsets
from shop.api.serializers import ProductSerializer
from shop.models import *
class ProductCRUDCBV(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer