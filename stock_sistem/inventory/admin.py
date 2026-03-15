from django.contrib import admin
from .models import Product, Counterparty, StockMovement
from django.urls import reverse
from django.utils.html import format_html


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'movement_type',
        'quantity',
        'price',
        'created_at',
        'counterparty',
        'total_value',
        'copy_button',
        'comment'
    )

    change_list_template = "inventory/stockmovement_changelist.html"

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name='Manager').exists():
            return False
        return super().has_delete_permission(request, obj)

    def copy_button(self, obj):

        if obj.pk:
            return format_html(
                '<a class="button" href="{}">Копіювати</a>',
                reverse('copy_movement', args=[obj.pk])
            )

        return "-"

    copy_button.short_description = "Копія"


admin.site.register(Product)
admin.site.register(Counterparty)