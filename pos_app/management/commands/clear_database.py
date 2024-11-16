from django.core.management.base import BaseCommand
from pos_app.models import Department, Position, Employees, Category, Products, salesItems, ReturnedProducts

class Command(BaseCommand):
    help = 'Clears all data from the database'

    def handle(self, *args, **kwargs):
        # Delete data in the tables
        self.stdout.write(self.style.SUCCESS("Deleting data from Departments..."))
        Department.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleting data from Positions..."))
        Position.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleting data from Employees..."))
        Employees.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleting data from Categories..."))
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleting data from Products..."))
        Products.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleting data from SalesItems..."))
        salesItems.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deleting data from ReturnedProducts..."))
        ReturnedProducts.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All data cleared successfully."))
