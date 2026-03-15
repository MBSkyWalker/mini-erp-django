from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
class Counterparty(models.Model):
    COUNTERPARTY_TYPES = (
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=COUNTERPARTY_TYPES)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_stock = models.PositiveIntegerField(default=5)

    def get_stock_balance(self):
        from django.db.models import Sum

        incoming = self.stockmovement_set.filter(
            movement_type='in'
        ).aggregate(total=Sum('quantity'))['total'] or 0

        outgoing = self.stockmovement_set.filter(
            movement_type='out'
        ).aggregate(total=Sum('quantity'))['total'] or 0

        return incoming - outgoing
    
    def is_below_min_stock(self):
        return self.get_stock_balance() < self.min_stock
    

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Incoming'),
        ('out', 'Outgoing'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    counterparty = models.ForeignKey(
        Counterparty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # актуальна закупочна 
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    
    
    

    def clean(self):
        if self.movement_type == 'out':
            current_balance = self.product.get_stock_balance()
            
            if self.quantity > current_balance:
                raise ValidationError(
                    f"Not enough stock. Available: {current_balance}")
            
            # new_balance = current_balance - self.quantity
            # if new_balance < self.product.min_stock:
            #     print(f'you need to buy more {self.product.name} cause you have only {new_balance}')
            # else:
            #     print('you have enough')
            #     print(new_balance, self.product.min_stock)

        if self.price is None:
            if self.movement_type == 'in':
                self.price = self.product.purchase_price
            else:
                self.price = self.product.selling_price

    @property
    def total_value(self):
        if self.price is None:
            return 0
        return self.price * self.quantity
    
    @property
    def profit(self):
        if self.movement_type == 'out' and self.price and self.purchase_price:
            return (self.price - self.purchase_price) * self.quantity
        return 0
    
    def save(self, *args, **kwargs):

        if not self.pk:
            if self.movement_type == 'out':
                if not self.price:
                    self.price = self.product.selling_price

                if not self.purchase_price:
                    self.purchase_price = self.product.purchase_price

            elif self.movement_type == 'in':
                if not self.purchase_price:
                    self.purchase_price = self.product.purchase_price

        super().save(*args, **kwargs)
    
class SalesReport(models.Model):
    date = models.DateField(default=timezone.now)
    total_quantity = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Звіт за {self.date}"

