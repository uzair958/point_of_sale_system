from django.core.management.base import BaseCommand
from pos_app.models import Department, Position, Employees, Category, Products, Product, salesItems, ReturnedProducts, product_sold_record

class Command(BaseCommand):
    help = 'Deletes all the sample data from the database'

    def handle(self, *args, **kwargs):
        # Deleting Product Sold Records first, as they reference Products and Product Codes
        product_sold_record.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all product sold records.'))

        # Deleting Returned Products
        ReturnedProducts.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all returned products.'))

        # Deleting Sales Items
        salesItems.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all sales items.'))

        # Deleting Product Codes
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all product codes.'))

        # Deleting Products
        Products.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all products.'))

        # Deleting Categories
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all categories.'))

        # Deleting Employees
        Employees.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all employees.'))

        # Deleting Positions
        Position.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all positions.'))

        # Deleting Departments
        Department.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all departments.'))

        self.stdout.write(self.style.SUCCESS("All sample data has been successfully deleted."))
