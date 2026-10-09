from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsApprovedSellerOrReadOnly


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsApprovedSellerOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'seller',
            'category',
        )

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by('name')

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsApprovedSellerOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.select_related('seller', 'category')

        # Buyers and anonymous users can access active products.
        # Sellers can also retrieve their own inactive products.
        if (
            self.request.user.is_authenticated
            and self.request.user.role == 'SELLER'
        ):
            return queryset.filter(seller=self.request.user)

        return queryset.filter(is_active=True)