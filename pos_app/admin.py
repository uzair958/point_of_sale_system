import re
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Employees, Category, Products, salesItems, Department, Position, ReturnedProducts,Product, product_sold_record

# Register each model with the admin site
admin.site.register(Employees)
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(salesItems)
admin.site.register(Department)
admin.site.register(Position)
admin.site.register(ReturnedProducts)
admin.site.register(Product)
admin.site.register(product_sold_record)
# admin.site.site_header = 'POS SYSTEM'

