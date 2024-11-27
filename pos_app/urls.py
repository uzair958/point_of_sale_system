from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
  
   
path('', views.inventory_view, name='inventory'),
path('pos/', views.pos_view, name='pos'),
path('return-product/', views.return_product_view, name='return_product'),
path('dashboard/', views.analysis_dashboard, name='analysis_dashboard'),
path('login/', views.login_view, name='login'),
path('logout/', views.custom_logout_view, name='logout'),
path('delete-old-products/', views.delete_old_sold_products, name='delete_old_products'),


]