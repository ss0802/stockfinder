from django.db import models
from django.contrib.auth.models import User

class StockBasket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    basket = models.ForeignKey(StockBasket, on_delete=models.CASCADE, related_name='stocks')
    symbol = models.CharField(max_length=20)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol
