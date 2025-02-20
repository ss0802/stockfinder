from django.urls import path
from .views import portfolio_dashboard, create_basket, add_stock

urlpatterns = [
    path('', portfolio_dashboard, name='portfolio_dashboard'),
    path('create_basket/', create_basket, name='create_basket'),
    path('add_stock/<int:basket_id>/', add_stock, name='add_stock'),
]