from django.contrib import admin

from products.models import Product, ProductVote

admin.site.register(Product)
admin.site.register(ProductVote)
