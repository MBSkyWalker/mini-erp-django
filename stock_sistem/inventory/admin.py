from django.contrib import admin
from .models import Product, Counterparty, StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'price','created_at', 'counterparty', 'total_value' )
    change_list_template = "inventory/stockmovement_changelist.html"  # кастомний шаблон

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name='Manager').exists():
            return False
        return super().has_delete_permission(request, obj)

admin.site.register(Counterparty)

admin.site.register(Product)