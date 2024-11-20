from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import login_required decorator
from django.db.models import F, ExpressionWrapper, FloatField
from .models import Products, salesItems, ReturnedProducts, Category, Employees
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


# @login_required

def pos_view(request):

    if 'employee_id' not in request.session:
        # Redirect to login page if not logged in
        return redirect('login')

    products_info = []  # List to store details of each added product
    grand_total = 0
    tax_rate = 0.02  # 2% tax rate
    error_message = None  # To store any error messages

    if request.method == "POST":
        product_codes = request.POST.getlist("product_code")
        quantities = request.POST.getlist("quantity")

        for code, qty in zip(product_codes, quantities):
            if code and qty.isdigit():  # Check that code is valid and quantity is numeric
                qty = int(qty)
                try:
                    product = Products.objects.get(code=code)

                    # Check if the product has enough stock
                    if product.qty < qty:
                        error_message = f"Not enough stock for product {product.name}. Only {product.qty} available."
                        break  # Stop processing further sales if any product has insufficient stock
                    
                    price = product.price
                    total_price = price * qty
                    grand_total += total_price

                    # Update or create an entry in salesItems table
                    sales_item, created = salesItems.objects.get_or_create(
                        product_id=product,
                        defaults={'qty': 0, 'total': 0, 'price': price}
                    )

                    # Update quantity and total for the product in salesItems
                    sales_item.qty += qty
                    sales_item.total += total_price
                    sales_item.save()

                    # Reduce the product quantity in stock
                    product.qty -= qty
                    product.save()

                    # Store each product's information to be displayed in the template
                    products_info.append({
                        'code': code,
                        'name': product.name,
                        'price': price,
                        'quantity': qty,
                        'total_price': total_price,
                    })
                except Products.DoesNotExist:
                    products_info.append({
                        'code': code,
                        'name': "Product not found",
                        'price': 0,
                        'quantity': qty,
                        'total_price': 0,
                    })

        # Calculate tax and final total if no error
        if not error_message:
            tax_amount = grand_total * tax_rate
            final_total = grand_total + tax_amount
        else:
            tax_amount = 0
            final_total = 0

    else:
        tax_amount = 0
        final_total = 0

    context = {
        'products_info': products_info,
        'grand_total': grand_total,
        'tax_amount': tax_amount,
        'final_total': final_total,
        'tax_rate': tax_rate * 100,  # Display as percentage
        'error_message': error_message  # Include the error message in the context
    }

    return render(request, 'pos.html', context)



# @login_required
def return_product_view(request):
    if 'employee_id' not in request.session:
        # Redirect to login page if not logged in
        return redirect('login')
    products_info = []  # To store information about each returned product
    error_message = None

    if request.method == "POST":
        product_codes = request.POST.getlist("product_code")  # List of product codes
        quantities = request.POST.getlist("quantity")  # List of quantities for each product code

        for code, qty in zip(product_codes, quantities):
            if code and qty.isdigit():  # Check that the code is not empty and quantity is numeric
                qty = int(qty)  # Convert quantity to integer
                try:
                    # 1. Get the product from the Products table
                    product = Products.objects.get(code=code)

                    # 2. Check the quantity sold
                    sales_item = salesItems.objects.get(product_id=product)
                    if sales_item.qty < qty:
                        error_message = f"The quantity returned exceeds the quantity sold for product {code}."
                        break  # Exit the loop without updating the inventory or sales record

                    # 3. If quantity is valid, proceed with the return process
                    # Update the product's inventory in the Products table
                    product.qty += qty  # Add returned quantity to inventory
                    product.save()  # Save the updated quantity

                    # 4. Update or create an entry in the ReturnedProducts table
                    returned_product, created = ReturnedProducts.objects.get_or_create(
                        product=product,
                        defaults={'quantity': qty}
                    )
                    if not created:
                        # If the entry exists, add the returned quantity to the existing quantity
                        returned_product.quantity += qty
                        returned_product.save()

                    # 5. Update the salesItems table to reflect the returned quantity
                    sales_item.qty -= qty  # Decrease the sold quantity by the returned amount
                    sales_item.total -= (product.price * qty)  # Adjust the total based on the returned quantity
                    sales_item.save()

                    # Append product info for display in the template
                    products_info.append({
                        'product': product,
                        'returned_qty': qty,
                        'new_qty': product.qty,
                    })
                except Products.DoesNotExist:
                    error_message = f"Product with code {code} does not exist."
                except salesItems.DoesNotExist:
                    error_message = f"No sales record found for product {code}."

    # Send back the result (products info, error message)
    context = {
        'products_info': products_info,
        'error_message': error_message,
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