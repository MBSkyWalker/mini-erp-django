from django.urls import path
from .views import stock_report, home, today_sales_report
from . import views

urlpatterns = [
    path('stock-report/', stock_report, name='stock_report'),
    path('', home, name="home"),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('sales-report',today_sales_report, name='today_sales_report' ),
    path('report/', views.period_sales_report, name='period_report'),
    path('movement/<int:pk>/copy/', views.copy_movement, name='copy_movement')
]