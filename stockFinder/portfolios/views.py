from django.shortcuts import render, redirect
from .models import StockBasket, Stock
from django.contrib.auth.decorators import login_required

@login_required
def portfolio_dashboard(request):
    baskets = StockBasket.objects.filter(user=request.user)
    return render(request, 'portfolios/dashboard.html', {'baskets': baskets})

@login_required
def create_basket(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            StockBasket.objects.create(user=request.user, name=name)
        return redirect('portfolio_dashboard')
    return render(request, 'portfolios/create_basket.html')

@login_required
def add_stock(request, basket_id):
    basket = StockBasket.objects.get(id=basket_id)
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        if symbol:
            Stock.objects.create(basket=basket, symbol=symbol)
        return redirect('portfolio_dashboard')
    return render(request, 'portfolios/add_stock.html', {'basket': basket})