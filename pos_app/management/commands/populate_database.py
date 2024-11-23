import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from pos_app.models import Department, Position, Employees, Category, Products, Product, salesItems, ReturnedProducts, product_sold_record

fake = Faker()

class Command(BaseCommand):
    help = 'Populates the database with random sample data'

    def handle(self, *args, **kwargs):
        # Create Departments
        departments = []
        for _ in range(5):
            department = Department.objects.create(
                name=fake.company(),
                description=fake.text(),
                status=random.choice([0, 1]),
                date_added=timezone.now(),
                date_updated=timezone.now()
            )
            departments.append(department)

        # Create Positions
        positions = []
        for dept in departments:
            for _ in range(3):  # Add 3 positions per department
                position = Position.objects.create(
                    title=fake.job(),
                    department=dept,
                    description=fake.text(),
                    status=random.choice([0, 1]),
                    date_added=timezone.now(),
                    date_updated=timezone.now()
                )
                positions.append(position)

        # Create Employees
        employees = []
        for _ in range(20):  # Create 20 employees
            employee = Employees.objects.create(
                code=fake.unique.uuid4(),
                password=fake.password(),
                firstname=fake.first_name(),
                middlename=fake.first_name(),
                lastname=fake.last_name(),
                gender=random.choice(['Male', 'Female']),
                dob=fake.date_of_birth(minimum_age=18, maximum_age=65),
                contact=fake.phone_number(),
                address=fake.address(),
                email=fake.email(),
                department_id=random.choice(departments),
                position_id=random.choice(positions),
                date_hired=fake.date_this_decade(),
                salary=round(random.uniform(30000, 120000), 2),
                status=random.choice([0, 1]),
                date_added=timezone.now(),
                date_updated=timezone.now()
            )
            employees.append(employee)

        # Create Categories
        categories = []
        for _ in range(5):  # Create 5 categories
            category = Category.objects.create(
                name=fake.word(),
                description=fake.text(),
                status=random.choice([0, 1]),
                date_added=timezone.now(),
                date_updated=timezone.now()
            )
            categories.append(category)

        # Create Products
        products = []
        for category in categories:
            for _ in range(5):  # Add 5 products per category
                product = Products.objects.create(
                    code=fake.unique.ean(length=13),  # Adjusted to EAN-13 length
                    category_id=category,
                    name=fake.word(),
                    description=fake.text(),
                    price=round(random.uniform(10, 1000), 2),
                    qty=random.randint(1, 100),
                    status=random.choice([0, 1]),
                    date_added=timezone.now(),
                    date_updated=timezone.now()
                )
                products.append(product)

        # Create Product Codes
        product_codes = []
        for product in products:
            product_code = Product.objects.create(
                code=fake.unique.uuid4(),
                product_id=product
            )
            product_codes.append(product_code)

        # Create Sales Items
        for product in products:
            salesItems.objects.create(
                category_id=product.category_id,
                product_id=product,
                price=product.price,
                qty=random.randint(1, 5),
                total=round(product.price * random.randint(1, 5), 2)
            )

        # Create Returned Products
        for product in products[:10]:  # Create 10 returned products
            ReturnedProducts.objects.create(
                product=product,
                quantity=random.randint(1, 10),
                date_returned=timezone.now()
            )

        # Create Product Sold Records
        for product_code in product_codes[:15]:  # Create 15 sold records
            product_sold_record.objects.create(
                codes=product_code.code,
                product_info=product_code.product_id,
                date=fake.date_this_year(),
                price=round(random.uniform(10, 1000), 2)  # Assuming price needs to be associated with sold record
            )

        self.stdout.write(self.style.SUCCESS("Database populated with random sample data successfully."))
