import code
from datetime import datetime
from itertools import product
from math import prod
from pyexpat import model
from re import U
from unicodedata import category, decimal
from django.db import models
from django.utils import timezone

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=255)  # Name of the department, unique
    description = models.TextField(blank=True, null=True)  # Optional description of the department
    status = models.IntegerField(default=1)  # Active status, e.g., 1 for active, 0 for inactive
    date_added = models.DateTimeField(default=timezone.now)  # Timestamp when the department was created
    date_updated = models.DateTimeField(auto_now=True) 
    
    
class Position(models.Model):
    title = models.CharField(max_length=255)  # Position title (e.g., "Manager", "Developer")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)  # Link to Department
    description = models.TextField(blank=True, null=True)  # Optional description of the position
    status = models.IntegerField(default=1)  # Active status, e.g., 1 for active, 0 for inactive
    date_added = models.DateTimeField(default=timezone.now)  # Timestamp when the position was created
    date_updated = models.DateTimeField(auto_now=True)  # Timestamp when the position was last updated
 # Timestamp when the department was last updated

    def __str__(self):
        return self.title
class Employees(models.Model):
    code = models.CharField(max_length=100,unique=True,null=False) 
    password= models.CharField(max_length=100,unique=True,null=False)
    firstname = models.TextField() 
    middlename = models.TextField(blank=True,null= True) 
    lastname = models.TextField() 
    gender = models.TextField(blank=True,null= True) 
    dob = models.DateField(blank=True,null= True) 
    contact = models.TextField() 
    address = models.TextField() 
    email = models.TextField() 
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE) 
    position_id = models.ForeignKey(Position, on_delete=models.CASCADE) 
    date_hired = models.DateField() 
    salary = models.FloatField(default=0) 
    status = models.IntegerField() 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.firstname + ' ' +self.middlename + ' '+self.lastname + ' '
    
class Category(models.Model):
    name = models.TextField()
    description = models.TextField(blank= True, null= True)
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name



class Products(models.Model):
    code = models.CharField(max_length=100,unique=True) 
    name = models.TextField()
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.FloatField(default=0) 
    status = models.IntegerField(default=1)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    qty = models.IntegerField(default=0)
    
    def __str__(self):
        return  self.name
    
class Product(models.Model):
    code = models.CharField(max_length=100,unique=True)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return self.code + " - " + self.product_id.name
    
    
class salesItems(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0)
    total = models.FloatField(default=0)
    

class ReturnedProducts(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)  # Link to the Products table
    quantity = models.PositiveIntegerField(default=0)  # Quantity of returned product
    date_returned = models.DateTimeField(default=timezone.now)  # Date when the product was returned

    def __str__(self):
        return f"{self.product.name} - Returned Quantity: {self.quantity}"

class product_sold_record(models.Model):
    codes= models.CharField(max_length=100,unique=True)
    product_info= models.ForeignKey(Products, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    price= models.FloatField(default=0)

