from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'open_price', 'high_price', 'low_price', 'last_price', 'volume', 'unusual_activity')