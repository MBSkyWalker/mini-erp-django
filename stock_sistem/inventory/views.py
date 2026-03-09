from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, StockMovement, SalesReport
from django.utils import timezone
from django.db.models import Sum, F
from datetime import datetime

def home(request):
    return render(request, 'inventory/home.html')

def stock_report(request):
    products = Product.objects.all()

    # 🔎 Пошук по назві
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    data = []

    for product in products:
        balance = product.get_stock_balance()
        is_low = product.is_below_min_stock()


        # 📦 Фільтр "тільки в наявності"
        in_stock = request.GET.get('in_stock')
        if in_stock == '1' and balance <= 0:
            continue
        
        
            

        data.append({
            'name': product.name,
            'balance': balance,
            'purchase_price': product.purchase_price,
            'selling_price': product.selling_price,
            'product_id':product.id,
            'is_low':is_low
            
        })

    


    return render(
        request,
        'inventory/stock_report.html',
        {
            'products': data,
            'search_query': search_query,
            'in_stock': request.GET.get('in_stock')
        }
    )

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.stockmovement_set.all().order_by('-created_at')

    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'movements': movements
    })

def today_sales_report(request):
     today = timezone.now().date()
     sales = StockMovement.objects.filter( movement_type='out', created_at__date=today )
     total_quantity = sales.aggregate( total_qty=Sum('quantity') )['total_qty'] or 0
     total_revenue = sales.aggregate( total_sum=Sum(F('quantity') * F('price')) )['total_sum'] or 0
     total_profit = sum(s.profit for s in sales) / 2

     report, created = SalesReport.objects.get_or_create(date=today, 
                                                        defaults={
        'total_quantity': total_quantity,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
    }
)
     if not created:
        report.total_quantity = total_quantity
        report.total_revenue = total_revenue
        report.total_profit = total_profit
        report.save()


     return render(request, 'inventory/today_sales.html', { 'sales': sales, 'total_quantity': total_quantity, 'total_revenue': total_revenue, 'today': today, 'total_profit':total_profit } )
    

def period_sales_report(request):
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    print(f'start date: {start_date}, end_date: {end_date} ')
    

    reports = SalesReport.objects.all()

    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # робимо timezone-aware
        

        reports = SalesReport.objects.filter(
            created_at__range=[start_date, end_date]
        ).order_by('date')
        
    for report in reports:
        report_date = report.date

        report.sales = StockMovement.objects.filter(
            movement_type='out',
            created_at__date=report_date
        )
    # else:
    #     reports = SalesReport.objects.all().order_by('created_at')
    
    return render(request, 'inventory/period_report.html', {
    'reports': reports,
    
})

def copy_movement(request, pk):

    movement = get_object_or_404(StockMovement, pk=pk)

    movement.pk = None
    movement.save()

    return redirect("/admin/inventory/stockmovement/")
    
    
   