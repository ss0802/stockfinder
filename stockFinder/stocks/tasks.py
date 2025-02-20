from celery import shared_task
import yfinance as yf
from .models import Stock

@shared_task
def update_stock_data():
    stocks = Stock.objects.all()
    for stock in stocks:
        try:
            data = yf