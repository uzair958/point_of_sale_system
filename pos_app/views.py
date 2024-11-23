from calendar import c
from itertools import count
from math import prod
from re import I
from tabnanny import check
from tkinter import N
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import login_required decorator
from django.db.models import F, ExpressionWrapper, FloatField
from .models import Products, Product, product_sold_record, salesItems, ReturnedProducts, Category, Employees
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employees
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse
from .models import Employees
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import F, Sum


def custom_logout_view(request):
    logout(request)  # Logs out the user
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Redirect to login or any other page



def login_view(request):
    if request.method == "POST":
        if "login" in request.POST:
            code = request.POST.get("code")
            password = request.POST.get("password")
            
            try:
                # Find the employee and verify credentials
                employee = Employees.objects.get(code=code, password=password)
                
                # Manually set the session for the employee
                request.session['employee_id'] = employee.id  # Storing employee ID in session
                employee.last_login = timezone.now()
                employee.save()  # Update the last login timestamp
                
                # Check and redirect to next URL or default to inventory
                next_url = request.GET.get('next')  # Debugging: Check the value of 'next' parameter
                return redirect(next_url if next_url else 'inventory')
                
            except Employees.DoesNotExist:
                messages.error(request, "Invalid code or password.")

    return render(request, 'login.html')



# @login_required
def inventory_view(request):
    # if 'employee_id' not in request.session:
    #     # Redirect to login page if not logged in
    #     return redirect('login')
    products = Products.objects.filter(status=1)  # Filter to show only available items
    return render(request, 'inventory.html', {'products': products})




def pos_view(request):
    if 'employee_id' not in request.session:
        # Redirect to login page if not logged in
        return redirect('login')

    products_info = []  # List to store details of each added product
    grand_total = 0
    tax_rate = 0.02  # 2% tax rate
    error_message = None 
    product_summary = {}  # Dictionary to hold aggregated product data

    if request.method == "POST":
        product_codes = request.POST.getlist("product_code")
        
        for code in product_codes:
            try:
                # Get the product using the product code
                product = Product.objects.get(code=code)

                # Check if the product has already been sold (based on unique code)
                if product_sold_record.objects.filter(codes=code).exists():
                    error_message = f"Product with code '{code}' has already been sold."
                    break
                elif not product:
                    error_message = f"Product with code '{code}' does not exist."
                    break

                # Aggregate the product data
                if code in product_summary:
                    product_summary[code]['quantity'] += 1
                    product_summary[code]['total_price'] += product.product_id.price
                else:
                    product_summary[code] = {
                        'name': product.product_id.name,
                        'price': product.product_id.price,
                        'quantity': 1,
                        'total_price': product.product_id.price
                    }

            except Product.DoesNotExist:
                error_message = f"Product with code '{code}' does not exist."
                break

        if error_message:
            return render(request, 'pos.html', {'error_message': error_message})

        # Now, process the aggregated product data and update sales records
        for code, data in product_summary.items():
            try:
                product=Product.objects.get(code=code)
                # Create a product_sold_record for each unique product
                product_sold_history = product_sold_record.objects.create(
                    codes=code,
                    product_info=product.product_id,
                    date=timezone.now(),
                    price=data['price'],
                )
                product_sold_history.save()

                # Update or create the sales item (aggregating sales)
                sales_item, created = salesItems.objects.get_or_create(
                    product_id=product.product_id,
                    category_id= Category.objects.get(id=product.product_id.category_id.id),
                    defaults={'qty': data['quantity'], 'total': data['total_price'], 'price': data['price']}
                )
                if not created:
                    sales_item.qty += data['quantity']
                    sales_item.total += data['total_price']
                    sales_item.save()

                # Update stock quantity for the product
                product.product_id.qty -= data['quantity']
                product.save()

                # Store the product information for the template
                products_info.append({
                    'general_code': code,
                    'name': data['name'],
                    'price': data['price'],
                    'quantity': data['quantity'],
                    'total_price': data['total_price'],
                })

            except Exception as e:
                error_message = f"An error occurred while processing product code '{code}': {e}"
                break

        if error_message:
            return render(request, 'pos.html', {'error_message': error_message})

        # Calculate tax and final total
        grand_total = sum(item['total_price'] for item in products_info)
        tax_amount = grand_total * tax_rate
        final_total = grand_total + tax_amount

        context = {
            'products_info': products_info,
            'grand_total': grand_total,
            'tax_amount': tax_amount,
            'final_total': final_total,
            'tax_rate': tax_rate * 100,  # Display tax rate as percentage
            'date': timezone.now(),
        }

    else:
        # Handle GET request with default values
        context = {
            'products_info': [],
            'grand_total': 0,
            'tax_amount': 0,
            'final_total': 0,
            'tax_rate': tax_rate * 100,
            'date': timezone.now(),
        }

    return render(request, 'pos.html', context)

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta

def return_product_view(request):
    if 'employee_id' not in request.session:
        # Redirect to login page if not logged in
        return redirect('login')
    
    products_info = None  # To store information about each returned product
    error_message = None

    if request.method == "POST":
        product_codes = request.POST.getlist("product_code")  # List of product codes

        for code in product_codes:
            try:
                # Fetch the sold product record
                prod=Product.objects.get(code=code)
                product_sold_history = product_sold_record.objects.get(codes=code)
                product = product_sold_history.product_info

                # Check if the product has enough quantity sold
                sales_item = salesItems.objects.get(product_id=product)
                if sales_item.qty < 1:
                    error_message = f"The quantity returned exceeds the quantity sold for product {code}."
                    break

                # Ensure the return is within the allowed time frame (2 days)
                two_days_ago = product_sold_history.date - timedelta(days=2)
                if product_sold_history.date < two_days_ago:

                    error_message = f"The product {code} exceeds the 2-day return limit."
                    break

                # Update product inventory in the Products table
                product.qty += 1
                product.save()

                # Update or create an entry in the ReturnedProducts table
                returned_product, created = ReturnedProducts.objects.get_or_create(
                    product=product,
                    defaults={'quantity': 1}
                )
                if not created:
                    returned_product.quantity += 1
                    returned_product.save()

                # Update salesItems to reflect the returned quantity
                sales_item.qty -= 1
                sales_item.total -= product.price
                sales_item.save()

                # Remove the product from the sold records
                product_sold_record.objects.get(codes=code).delete()

                # Set success message
               

            except product_sold_record.DoesNotExist:
                error_message = f"Product with code {code} does not exist in the sales history."
                break
            except salesItems.DoesNotExist:
                error_message = f"No sales record found for product {code}."
                break
            except prod.DoesNotExist:
                error_message = f"Product with code {code} does not exist."
                break

            except Exception as e:
                error_message = str(e)
                break

            products_info = 'Return Successful'
    # Prepare the context for rendering the response
    context = {
        'error_message': error_message,
        'products_info': products_info
    }

    return render(request, 'return_product.html', context)




# @login_required


def analysis_dashboard(request):

    if 'employee_id' not in request.session:
        # Redirect to login page if not logged in
        return redirect('login')
    
    # 1. Top 5 Products Sold by Quantity (considering the returns)
    top_products_sold = (
        salesItems.objects.values('product_id__name')
        .annotate(total_sold=Sum('qty'))
        .order_by('-total_sold')[:5]
    )

    # 2. Top 5 Products Returned by Quantity
    top_returned_products = (
        ReturnedProducts.objects.values('product__name', 'quantity')
        .order_by('-quantity')[:5]
    )

    # 3. Top 5 Products by Initial to Current Quantity Ratio
    top_products_ratio = (
        Products.objects.annotate(
            total_sold=F('salesitems__qty'),  # Total quantity sold (assuming cumulative in salesItems)
            initial_quantity=F('qty') + F('salesitems__qty'),  # Initial quantity = current + total sold
            current_quantity=F('qty'),  # Current quantity is just the current stock in Products table
            ratio=ExpressionWrapper(
                (F('qty') + F('salesitems__qty')) / F('qty'),
                output_field=FloatField()
            )
        )
        .order_by('-ratio')[:5]
    )

    # 4. Top 5 Categories by Popularity (Quantity Sold)
    top_categories = (
        salesItems.objects.values('product_id__category_id__name')
        .annotate(total_sold=Sum('qty'))
        .order_by('-total_sold')[:5]
    )

    # 5. Totals: Total Employees, Total Categories, Total Products
    total_employees = Employees.objects.count()
    total_categories = Category.objects.count()
    total_products = Products.objects.count()

    context = {
        'top_products_sold': top_products_sold,
        'top_returned_products': top_returned_products,
        'top_products_ratio': top_products_ratio,
        'top_categories': top_categories,
        'total_employees': total_employees,
        'total_categories': total_categories,
        'total_products': total_products,
    }

    return render(request, 'analysis_dashboard.html', context)

def custom_logout_view(request):
    messages.info(request, "You have been logged out successfully.")
    logout(request)  # Logs out the user
    return redirect('login')